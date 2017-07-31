import logging.config
import multiprocessing
import os
import shutil
import time
from argparse import ArgumentParser
from configparser import ConfigParser

import pandas as pd
from competitions import CompetitionPage


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_cities_folder(base_path):
    cities_list = os.listdir(base_path)
    if '.DS_Store' in cities_list:
        cities_list.remove('.DS_Store')
    return cities_list


class MyVstupDataProvider(object):
    def __init__(self, data_base_path: str):

        self.competition_path_template = os.path.join(
            data_base_path,
            '{city}/{university}/{competition}/data.csv')
        self.faculty_info_path_template = os.path.join(
            data_base_path,
            '{city}/{university}/_faculty_info.csv')
        self.university_info_path_template = os.path.join(
            data_base_path,
            '{city}/{university}/_university_info.csv')

    def competition(self, city, university, competition):
        file_path = self.competition_path_template.format(city,
                                                          university,
                                                          competition)
        if os.path.exists(file_path):
            return pd.read_csv(file_path)

    def university_info(self, city, university):
        file_path = self.university_info_path_template.format(city,
                                                              university)
        if os.path.exists(file_path):
            return pd.read_csv(file_path)

    def faculty_info(self, city, university):
        file_path = self.faculty_info_path_template.format(city,
                                                           university)
        if os.path.exists(file_path):
            return pd.read_csv(file_path)


def get_competition_links(university_path):

    try:
        university_info_pdf = pd.read_csv(
            os.path.join(university_path, "_faculties_info.csv")
        )
        competition_links_list = university_info_pdf.competition_link.unique().tolist()
        return competition_links_list

    except Exception as e:
        logger.info("Can not read university info. Error %s" % e)
        return False


def populate_competition_info(university_path, competition_links_list):
    to_remove = os.listdir(university_path)
    if "_faculties_info.csv" in to_remove:
        to_remove.remove("_faculties_info.csv")
    if "_university_info.csv" in to_remove:
        to_remove.remove("_university_info.csv")
    if len(to_remove) != 0:
        for file in to_remove:
            shutil.rmtree(os.path.join(university_path, file), )

    counter = 0

    for link in competition_links_list:

        if link is not None:
            continue
        page = CompetitionPage()

        full_link = "http://www.vstup.info/2016/" + link[2:]
        logger.info("Working with {}".format(full_link))
        competition_pdf = page.get_data(full_link)

        if competition_pdf.shape[0] == 0:
            logger.warning("No table found at {}".format(full_link))
            continue

        competition_pdf = (competition_pdf
                           .replace(["—"], [None])
                           .where((pd.notnull(competition_pdf)), None))

        competition_folder = os.path.join(university_path, link.split("/")[-1][:-10])
        if not os.path.exists(competition_folder):
            os.mkdir(competition_folder)

        competition_pdf.to_csv(os.path.join(competition_folder, "competition.csv"), index=False)

        counter += 1
        logger.info("{} data points inserted from {}".format(competition_pdf.shape[0], full_link))
    logger.info("Done {} faculties.".format(counter))


def run_parser(city_list):
    for city in city_list:
        logger.info('Working with "{}"'.format(city))
        university_pathes = (city)

        for university in university_pathes:
            links_list = get_competition_links(university)

            if links_list:
                populate_competition_info(university, links_list)


if __name__ == "__main__":

    arg_parser = ArgumentParser('Parsing data from vstup.info')
    arg_parser.add_argument('-cf',
                            '--config_file',
                            help='Path to config file.',
                            default="./parser.conf")
    arg_parser.add_argument('-e',
                            '--environment',
                            help='Staging or production.',
                            default="staging")
    args = arg_parser.parse_args()

    start_time = time.time()
    # for multiprocessing

    # setting logger
    # try:
    logging.config.fileConfig("logging.conf")
    # except Exception as e:
    #     print("Failed setting up loggers with error {}".format(e))
    logger = logging.getLogger(__name__)

    # setting database
    cp = ConfigParser()
    cp.read(args.config_file)

    cities = get_cities_folder()

    # splitting cities in chunks for multiprocessing
    link_chunks = []
    chunk_size = int(len(cities) / 4) + 1
    link_chunks = list(chunks(cities, chunk_size))

    # starting parser in multiprocessing
    process_list = []
    for i in range(4):
        process = multiprocessing.Process(target=run_parser,
                                          args=(link_chunks[i],))
        process.start()
        process_list.append(process)

    for process in process_list:
        process.join()

    logger.info("Done in {} sec.".format(time.time() - start_time))
