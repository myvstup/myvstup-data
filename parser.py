import logging
import multiprocessing
import os
import re
from argparse import ArgumentParser

import numpy as np
import pandas as pd
import requests
from psycopg2.extensions import register_adapter, AsIs
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import *
from tools.multiproc_guard import add_engine_pidguard
from tools.multiproc_logging import install_mp_handler
from vnz_page_parsers import VNZPage


def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def get_logger():
    logging.basicConfig(level=logging.INFO,
                        datefmt="%Y-%m-%d%H:%M:%S",
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        filename='parser.log',
                        filemode='w')

    return logging.getLogger(__name__)


def configure_db(args):

    if args.local_db:
        engine = create_engine("mysql://niko_yakovlev:Golddesk23/07@127.0.0.1/myvstup",
                               echo=False, encoding='utf-8')
    else:
        engine = create_engine(os.getenv('DATABASE_MYVSTUP') + "?charset=utf8",
                               echo=False, encoding='utf-8')
    add_engine_pidguard(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session()


def clean_db():
    q = """SHOW TABLES;"""

    resp = session.execute(q)
    tables_names = [i[0] for i in resp]

    if len(tables_names) == 0:
        return

    if len(tables_names) != 0:
        session.execute(""" SET FOREIGN_KEY_CHECKS = 0; """)
        for city in tables_names:
            session.execute(""" TRUNCATE TABLE %s ;""" % city)
        session.execute(""" SET FOREIGN_KEY_CHECKS = 1; """)
        session.commit()


def populate_cities_table():
    logger.info("Populating cities...")
    data = get_city_links("http://vstup.info")

    session.add_all(
        [City(name=name, link=link) for name, link in data.items()]
    )
    session.commit()
    logger.info("Done %s cities" % len(data))
    logger.info("Now in db %s cities" % len(session.query(City).all()))


def get_city_links(link):
    html = requests.get(link).content.decode()
    html = re.sub('<a.*?href="(.*?)">(.*?)</a>', '\\1 \\2', html)

    table = pd.read_html(html)[0]
    links = table[0].map(lambda r: link + r.split(' ')[0])
    cities = table[0].map(lambda r: r.split('#reg')[-1].strip())

    return dict(zip(cities, links))


def populate_uni_info_table(cities=None):

    if cities:
        cities_obj = [c for c in session.query(City).filter(City.name.in_(cities))]
    else:
        cities_obj = session.query(City).all()
    for city in cities_obj:
        counter = 0
        logger.info('Working with "%s"' % city.name)
        try:
            uni_links = get_universities_links(city.link)
        except ValueError:
            logger.info("City %s does not have any university." % city.name)
            continue
        for ind, item in enumerate(uni_links):
            parser = VNZPage(logger)
            parser.parse_data(link=uni_links[ind][1])
            if parser.uni_info_table is not None:
                university = University(
                    name=str(parser.uni_info_table.ix['uni_name', 'uni_info']),
                    type=str(parser.uni_info_table.ix['uni_type', 'uni_info']),
                    address=str(parser.uni_info_table.ix['address', 'uni_info']),
                    phones=str(parser.uni_info_table.ix['phones', 'uni_info']),
                    website=str(parser.uni_info_table.ix['website', 'uni_info']),
                    email=str(parser.uni_info_table.ix['email', 'uni_info']),
                    link=str(uni_links[ind][1]))
                university.city = city
                session.add(university)
                session.commit()
            f_counter = 0
            if parser.data.shape[0] != 0:
                parser.data.reset_index(drop=True, inplace=True)
                logger.info("Number of faculties %s" % parser.data.shape[0])
                for row in parser.data.index:
                    faculty = Faculty(
                        study_type=parser.data.ix[row, 'study_type'],
                        free_places=parser.data.ix[row, 'free_places'],
                        paid_places=parser.data.ix[row, 'paid_places'],
                        competition_link=parser.data.ix[row, 'competition_link'],
                        num_applied=parser.data.ix[row, 'num_applied'],
                        num_entered=parser.data.ix[row, 'num_entered'],
                        num_recommended=parser.data.ix[row, 'num_recommended'],
                        required_subj=str(parser.data.ix[row, 'required_subj']),
                        degree=parser.data.ix[row, 'degree'],
                        degree_subname=parser.data.ix[row, 'degree_subname'],
                        faculty=parser.data.ix[row, 'faculty'],
                        specialization_1=parser.data.ix[row, 'specialization_1'],
                        specialization_2=parser.data.ix[row, 'specialization_2'])
                    faculty.university = university
                    session.add(faculty)
                    session.commit()
                    f_counter += 1
                logger.info("Done %s faculties in %s." % (f_counter, university.name))
            counter += 1

        logger.info("Done %s universities in %s." % (counter, city.name))


def get_universities_links(city_link):
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

    return list(zip(vnz, links, uni_type))


def run_parser(cities):
    global session
    session = configure_db(args)
    populate_uni_info_table(cities)


if __name__ == "__main__":

    arg_parser = ArgumentParser('Parsing data from vstup.info')
    arg_parser.add_argument('-c',
                            '--clean_db',
                            help='Drop all data from db',
                            action='store_true',
                            default=False)
    arg_parser.add_argument('-l',
                            '--local_db',
                            help='Create local db.',
                            action='store_true',
                            default=False)
    args = arg_parser.parse_args()

    install_mp_handler()
    logger = get_logger()

    register_adapter(np.int64, addapt_numpy_float64)
    session = configure_db(args)

    if args.clean_db:
        clean_db()

    populate_cities_table()
    cities = [city.name for city in session.query(City).all()]

    cities_chunks = []
    for i in range(2):
        cities_chunks += [cities[i * 14:(i + 1) * 14]]

    process_list = []
    for i in range(2):
        process = multiprocessing.Process(target=run_parser,
                                          args=(cities_chunks[i],))
        process.start()
        process_list.append(process)

    for process in process_list:
        process.join()
