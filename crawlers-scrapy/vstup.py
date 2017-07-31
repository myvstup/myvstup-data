# -*- coding: utf-8 -*-
import scrapy
import re
from database import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_URL = 'http://vstup.info/'
DB_PATH = "sqlite:///../data/vstup.db"

BASIC_INFO_DICT = {
    'Назва ВНЗ:': "name",
    'Тип ВНЗ:': "type",
    'Підпорядкування:': "root",
    'Поштовий індекс:': "postal_index",
    'Адреса:': "address",
    'Телефони:': "phones",
    'Веб-сайт:': "website",
    'E-mail:': "email"
}
FACULTY_INFO_DICT = {
    "ОКР": "degree",
    "Галузь": "domain",
    "Спеціальність": "specialization",
    "Факультет": "faculty"
}
FACULTY_COMPETITION_DICT = {
    "всього": "applied_number",
    "рекомендовано": "recommended_number",
    "зараховано": "entered_number",
    "Ліцензований": "available_places",
    "Обсяг": "free_places"
}
STUDENTS_INFO_DICT = {
    "Прізвище, ім'я, по-батькові абітурієнта": "name",
    "Пріоритет заяви": "priority",
    "Конкурсний бал": "points",
    "Деталізація конкурсного бала": "detailed_point",
    "Коефіцієнти, що застосовуються до заяви": "pk+ck",
    "Оригінали документів особи": "original_docs"
}
_ukr = "[а-я А-Я їґєіІ \’ \- \s+]"
_splitter = "(\,\s)"
DEMANDS_REGEX = r"(\d.\s)({}+)\s?\(?({}+)?{}?(балmin\s(\d+))?{}?(k=(\d\.\d+))?\)?".format(
    _ukr, _ukr, _splitter, _splitter
)


def configure_db(db_path):
    engine = create_engine(
        str(db_path),
        echo=False,
        encoding='utf-8')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
session = configure_db(DB_PATH)


class VstupSpider(scrapy.Spider):
    name = 'vstup'
    allowed_domains = ['vstup.info']
    start_urls = ['http://vstup.info/']

    def parse(self, response):
        for city_name, city_link in zip(
                response.css("table.tablesaw-stack a::text").extract(),
                response.css("table.tablesaw-stack a::attr(href)").re(".*.html")):
            city = City(name=city_name, link=response.urljoin(city_link))
            session.add(city)
            session.commit()

            if city_link is not None:
                self.logger.info("Working with {}.".format(city_name))
                yield response.follow(city_link, self.parse_school)

    def parse_school(self, response):

        city_name = response.css("div[title*=Вступна]::text").extract()[1]

        school_type_selectors = response.css("div.accordion-body")
        for selector in school_type_selectors:

            school_type = selector.css(
                "div.accordion-body::attr(id)"
            ).extract_first()

            self.logger.info("Working with {} in {}.".format(
                school_type, city_name
            ))
            for school_name, school_link in zip(
                    selector.css("div.accordion-body a::text").extract(),
                    selector.css("div.accordion-body a::attr(href)").extract()):
                school_link = response.urljoin(school_link)
                if school_link is not None:
                    self.logger.info("Working with {}.".format(school_name))

                    request = scrapy.http.request.Request(
                        school_link,
                        self.parse_school_info)
                    request.meta['city_name'] = city_name
                    yield request

    def parse_school_info(self, response):

        school_data = response.css("div.accordion-group")
        school_args = {}

        city_name = response.meta["city_name"]
        city = [i for i in session.query(City).filter(City.name.is_(city_name))][0]

        if len(school_data) == 0:
            yield self.logger.warn("{} is empty.".format(response.url))

        # basic school info
        school_info = school_data\
            .css("table.tablesaw")\
            .css("table.tablesaw-stack[*|id=about] tr")
        for faculty_selector in school_info:
            try:
                key, value = faculty_selector.css("td::text").extract()
                school_args.update({
                    BASIC_INFO_DICT[key]: value
                })
            except ValueError:
                pass

        school_args["link"] = response.url
        school = School(**school_args)
        school.city = city
        session.add(school)
        session.commit()

        # zaochna or ochna type of study
        faculty_tables_list = response\
            .css("table.tablesaw")\
            .css("table.tablesaw-stack")\
            .css("table.tablesaw-sortable")

        for table in faculty_tables_list:

            counter = 0
            study_type = table.css("::attr(id)").re("\D+")[0]
            for tr in table.css("tbody tr"):

                faculty_info_dict = {
                    "study_type": study_type
                }
                td_s_list = tr.css("td")

                # first column
                for faculty_info, faculty_info_key in FACULTY_INFO_DICT.items():
                    faculty_info_dict[faculty_info_key] = td_s_list[0].css(
                        "span[*|title={}]::text".format(faculty_info)
                    ).extract_first()
                faculty_info_dict["study_dates"] = td_s_list[0].re(
                    "(\d{2}\/\d{2}\/\d{4}\s\-\s\d{2}\/\d{2}\/\d{4})"
                )[0]
                faculty_info_dict["first_year_is"] = td_s_list[0].re(
                    "(Зарахування на \d курс.)"
                )[0][:-1]

                # second/third column
                for faculty_info, faculty_info_key in FACULTY_COMPETITION_DICT.items():
                    value = td_s_list[1:3].css(
                        "*[title*={}]::text".format(faculty_info)
                    ).extract_first()
                    if value is not None:
                        value = re.search("\d+", value.replace("\xa0", " "))
                        faculty_info_dict[faculty_info_key] = value[0]
                    else:
                        pass

                competition_link = td_s_list[1].css(
                    "a.button::attr(href)"
                ).extract_first()
                if competition_link is not None:
                    faculty_info_dict["competition_link"] = response.urljoin(competition_link)

                # forth column
                demands_list = []
                demands_match = re.finditer(
                    DEMANDS_REGEX,
                    "".join(td_s_list[3].css("::text").extract())
                )

                for match in demands_match:
                    demands_list += [{
                        "subject": match[2].strip(),
                        "exam_type": match[3],
                        "min_score": int(match[6]) if match[6] not in ["", None] else None,
                        "coef": float(match[9]) if match[9] not in ["", None] else None
                    }]
                faculty_info_dict['demanded_subjects'] = str(demands_list)

                faculty = Faculty(**faculty_info_dict)
                faculty.school = school
                session.add(faculty)
                session.commit()
                counter += 1
                if faculty_info_dict.get("competition_link", None) is not None:
                    request = scrapy.http.request.Request(
                        faculty_info_dict["competition_link"],
                        self.parse_competition)
                    request.meta['faculty_id'] = faculty.id
                    yield request

            self.logger.info("{} Done {} for '{}' study_type.".format(
                school_args['name'],
                counter,
                study_type
            ))
        else:
            self.logger.warning("{} has only description.".format(school_args['name']))

    def parse_competition(self, response):

        faculty = [i for i in session.query(Faculty).filter(
            Faculty.id.is_(
                response.meta["faculty_id"]
            ))][0]

        table_schema = response.css(
            "table.tablesaw-sortable thead tr th::attr(title)"
        ).extract()
        table_schema = [
            j for i in table_schema[1:] for j in STUDENTS_INFO_DICT[i].split("+")
        ]

        counter = 0
        tr_s = response.css("table.tablesaw-sortable tbody tr")
        # looping on each student
        for tr in tr_s:
            descriptive_data = tr.css("td::text").extract()[1:]
            descriptive_data.insert(
                table_schema.index("detailed_point"),
                str(tr.css(
                    "td span[*|data-toggle=tooltip]::text"
                ).extract())
            )
            student_args = dict(zip(table_schema, descriptive_data))

            student = Student(**student_args)
            student.faculty = faculty
            session.add(student)
            session.commit()
            counter += 1
        yield self.logger.info("Done {} students in {}".format(
            counter,
            faculty.faculty
        ))