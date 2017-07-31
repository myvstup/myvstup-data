import csv
import logging.config
import multiprocessing
import os
import re
import shutil
from argparse import ArgumentParser
from collections import namedtuple
from configparser import ConfigParser

import pandas as pd
import requests
from basic_info import VNZPage


def create_cities_folder():
    City = namedtuple('City', 'name link')

    def get_city_links(base_link):
        html = requests.get(base_link).content.decode()
        html = re.sub('<a.*?href="(.*?)">(.*?)</a>', '\\1 \\2', html)

        table = pd.read_html(html)[0]
        links = table[0].map(lambda r: base_link + r.split(' ')[0]).tolist()
        city_list = table[0].map(lambda r: r.split('#reg')[-1].strip()).tolist()

        return [City(city_list[k], links[k]) for k in range(0, len(links))]

    logger.info("Populating cities...")
    data = get_city_links("http://vstup.info")

    for city in data:
        os.mkdir("./data/{}".format(city.name))
        with open("./data/{}/_city_link.txt".format(city.name), "w") as f:
            f.write(city.link)

    logger.info("Done %s cities." % len(data))
    logger.info("Created %s city folders." % len(os.listdir("./data/")))
    return data


def get_universities_links(city_link):
    University = namedtuple('University', 'name link type')

    html = requests.get(city_link).content.decode()
    html = re.sub('<a.*?href="(.*?)">(.*?)</a>', '\\1 \\2', html)
    possible = ['університет', 'академія', 'інститут',
                'коледж', 'технікум']

    final_table = pd.DataFrame()
    for table in pd.read_html(html):
        temp = table[0].map(lambda r: r.split('#vnz')[-1]).tolist()
        temp = pd.Series([w for r in temp for w in r.split(' ')]) \
            .value_counts().ix[possible].sort_values()
        if temp.sum() > temp.shape[0] * 0.5:
            predicted_val = temp.index[0]
        else:
            predicted_val = 'інше'
        table = pd.DataFrame(table)
        table['uni_type'] = predicted_val

        final_table = final_table.append(table)

    links = final_table[0].map(lambda r: 'http://vstup.info/2016' + r.split(' ')[0][1:]).tolist()
    vnz = final_table[0].map(lambda r: r.split('#vnz')[-1].strip()).tolist()
    uni_type = final_table['uni_type'].tolist()

    return [University(vnz[j], links[j], uni_type[j]) for j in range(0, len(vnz))]


def populate_uni_info_table(city_list):

    for city in city_list:

        counter = 0
        logger.info('Working with "%s"' % city.name)

        try:
            university_list = get_universities_links(city.link)
        except ValueError:
            logger.info("City %s does not have any university." % city.name)
            continue

        with open("./data/{}/_universities_info.csv".format(city.name), "w") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(["name", "link", "uni_type"])
            csv_writer.writerows(university_list)

        for university in university_list:

            university_path = ""
            parser = VNZPage()
            parser.parse_data(link=university.link)

            if parser.uni_info_table is not None:

                university_path = "./data/{}/{}".format(city.name, university.name)
                if not os.path.exists(university_path):
                    os.mkdir(university_path)
                parser.uni_info_table.to_csv(university_path + "/_info.csv")

            f_counter = 0

            if parser.data.shape[0] != 0:

                parser.data.reset_index(drop=True, inplace=True)
                parser.data = parser.data.where((pd.notnull(parser.data)), None)
                logger.info("Number of faculties %s" % parser.data.shape[0])

                parser.data.to_csv(university_path + "/_faculties_info.csv", index=False)
                logger.info("Done %s faculties in %s." % (f_counter, university.name))

            counter += 1

        logger.info("Done %s universities in %s." % (counter, city.name))


def run_parser(city_list):
    populate_uni_info_table(city_list)


if __name__ == "__main__":

    arg_parser = ArgumentParser('Parsing data from vstup.info')
    arg_parser.add_argument('-c',
                            '--clean_run',
                            help='Drop all data from db',
                            action='store_true',
                            default=False)
    arg_parser.add_argument('-cf',
                            '--config_file',
                            help='Path to config file.',
                            default="./parser.conf")
    arg_parser.add_argument('-e',
                            '--environment',
                            help='Staging or production.',
                            default="staging")
    args = arg_parser.parse_args()

    # setting logger
    # try:
    logging.config.fileConfig("logging.conf")
    # except Exception as e:
    #     print("Failed setting up loggers with error {}".format(e))
    logger = logging.getLogger(__name__)

    cp = ConfigParser()
    cp.read(args.config_file)

    if args.environment in cp.get("environments", "keys").split(","):
        logger.info("Environment is set to {}".format(args.environment))
    else:
        logger.info("Wrong environment. Valid only : staging/production".format(args.environment))
        exit()

    # setting database
    if args.clean_run:
        shutil.rmtree("./data")
        os.mkdir("./data")
    # populating cities table
    cities = create_cities_folder()

    # splitting cities in chunks for multiprocessing
    cities_chunks = []
    for i in range(8):
        cities_chunks += [cities[i * 14:(i + 1) * 14]]

    # starting parser in multiprocessing
    process_list = []
    for i in range(8):
        process = multiprocessing.Process(target=run_parser,
                                          args=(cities_chunks[i],))
        process.start()
        process_list.append(process)

    for process in process_list:
        process.join()
