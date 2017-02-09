from logger import logger
import os
import requests
import re
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from argparse import ArgumentParser
from database import *
from competition_page_parsers import CompetitionPage
from vnz_page_parsers import VNZPage

Session = sessionmaker()


def configure_db(args):
    if args.local_db:
        engine = create_engine("../data/" + args.name + ".db",
                               echo=False, encoding='utf-8')
    else:
        engine = create_engine(os.getenv('POSTGRES_MYVSTUP'),
                               echo=False, encoding='utf-8')
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)


def clean_db():
    q = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
      AND table_type='BASE TABLE';"""
    session = Session()
    resp = session.execute(q)
    tables_names = [i[0] for i in resp]

    session.execute("TRUNCATE TABLE %s " % ','.join(tables_names))


def populate_cities_table():
    logger.info("Populating cities...")
    data = get_city_links("http://vstup.info")
    session = Session()

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
    session = Session()

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
            parser = VNZPage()
            parser.parse_data(link=uni_links[ind][1])
            if parser.uni_info_table is not None:
                university = University(
                    name=parser.uni_info_table.ix['uni_name', 'uni_info'],
                    type=parser.uni_info_table.ix['uni_type', 'uni_info'],
                    address=parser.uni_info_table.ix['address', 'uni_info'],
                    phones=parser.uni_info_table.ix['phones', 'uni_info'],
                    website=parser.uni_info_table.ix['website', 'uni_info'],
                    email=parser.uni_info_table.ix['email', 'uni_info'],
                    link=uni_links[ind][1])
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


if __name__ == "__main__":

    arg_parser = ArgumentParser('Parsing data from vstup.info')
    arg_parser.add_argument('-n',
                            '--name',
                            help='If provided - create new db w/ provided name.')
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

    configure_db(args)

    if args.clean_db and args.local_db:
        os.remove('../data/%s.db' % args.name)
    elif args.clean_db:
        clean_db()

    populate_cities_table()
    populate_uni_info_table()