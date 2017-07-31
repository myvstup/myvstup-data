import logging.config
import multiprocessing
import time
from argparse import ArgumentParser
from configparser import ConfigParser

import numpy as np
import pandas as pd
from competitions import CompetitionPage
from psycopg2.extensions import register_adapter, AsIs
from sqlalchemy import text as query_text

from database import *
from tools.multiproc_guard import add_engine_pidguard
from tools.multiproc_logging import install_mp_handler


def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def configure_db(db_path):
    engine = create_engine(str(db_path) + "?charset=utf8",
                           echo=False, encoding='utf-8')
    add_engine_pidguard(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session()


def get_competition_links():
    q = """SELECT id, competition_link FROM faculties;"""
    resp = session.execute(q)
    links_list = [j for j in resp]
    logger.info("Got {} links.".format(len(links_list)))
    return links_list


def populate_competition_info(links=None):
    parser = CompetitionPage()
    faculty_query = session.query(Faculty)
    counter = 0
    for faculty_id, link in links:
        if link == "":
            logger.warning("Wrong link for faculty_id = %s" % faculty_id)
            continue
        faculty = faculty_query.filter(query_text('id = %s' % faculty_id))[0]
        link = "http://www.vstup.info/2016/" + link[2:]
        logger.info("Working with {}".format(link))
        competition_pdf = parser.get_data(link)
        if competition_pdf.shape[0] == 0:
            logger.warning("No table found at {}".format(link))
            continue
        competition_pdf = (competition_pdf
                           .replace(["—"], [None])
                           .where((pd.notnull(competition_pdf)), None))
        for index in competition_pdf.index.tolist():
            student = Student(
                name=competition_pdf.ix[index, 'student_name'],
                priority=competition_pdf.ix[index, 'priority'],
                school_certificate=competition_pdf.ix[index, 'school_certificate'],
                points=competition_pdf.ix[index, 'student_points'],
                zno=competition_pdf.ix[index, 'student_zno'],
                entrance_points=competition_pdf.ix[index, 'enterance_points'],
                additional_points=competition_pdf.ix[index, 'aditional_points'],
                original_docs=competition_pdf.ix[index, 'original_docs']
            )
            student.faculty = faculty
            session.add(student)
            session.commit()
        counter += 1
        logger.info("{} data points inserted from {}".format(competition_pdf.shape[0], link))
    logger.info("Done {} faculties.".format(counter))


def run_parser(links_chunk):
    global session
    session = configure_db(DB_PATH)
    populate_competition_info(links_chunk)


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
    install_mp_handler()

    # setting logger
    # try:
    logging.config.fileConfig("logging.conf")
    # except Exception as e:
    #     print("Failed setting up loggers with error {}".format(e))
    logger = logging.getLogger(__name__)

    # register new type
    register_adapter(np.int64, addapt_numpy_float64)

    # setting database
    cp = ConfigParser()
    cp.read(args.config_file)

    if args.environment in cp.get("environments", "keys").split(","):
        logger.info("Environment is set to {}".format(args.environment))
    else:
        logger.info("Wrong environment. Valid only : staging/production".format(args.environment))
        exit()

    DB_PATH = cp.get("environment_{}".format(args.environment),
                     "DB_PATH")

    session = configure_db(DB_PATH)

    # populating cities table
    links = get_competition_links()

    # splitting cities in chunks for multiprocessing
    link_chunks = []
    chunk_size = int(len(links) / 2) + 1
    link_chunks = list(chunks(links, chunk_size))

    # starting parser in multiprocessing
    process_list = []
    for i in range(2):
        process = multiprocessing.Process(target=run_parser,
                                          args=(link_chunks[i],))
        process.start()
        process_list.append(process)

    for process in process_list:
        process.join()

    logger.info("Done in {} sec.".format(time.now() - start_time))