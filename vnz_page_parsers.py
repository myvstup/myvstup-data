from logger import logger
import pandas as pd
import re
import requests

UNI_INFO_MAPPER = {
    'Назва ВНЗ:': 'uni_name',
    'E-mail:': 'email',
    'Адреса:': 'address',
    'Веб-сайт:': 'website',
    'Поштовий індекс:': 'post_index',
    'Телефони:': 'phones',
    'Тип ВНЗ:': 'uni_type'
}


class VNZparser:
    def __init__(self):
        pass

    @staticmethod
    def combine_data(html_text, data_type):
        table = pd.DataFrame()
        for part in pd.read_html(html_text):
            table = table.append(part)

        table = table[table['Спеціальність'] != 'Спеціальність']
        table = table[
            table['Спеціальність'].map(
                lambda r: True if 'факультет:' in r.lower() else False
            )]
        table.reset_index(drop=True, inplace=True)
        table['study_type'] = data_type

        return table

    @staticmethod
    def parse_students_numbers(table):
        p = r'(заяв:\s(\d+))(реком\.:\s(\d+))?(зарах\.:\s(\d+))?(\.(.*[^\s конкурс]))?'

        table['Конкурс'] = table['Конкурс'].map(lambda r: r.replace('\xa0', ' '))

        table = table.join(
            pd.DataFrame(  # new dataframe with parsed text
                table['Конкурс'].map(lambda r: {  # iterating on 'Конкурс' column
                    'num_applied': re.compile(p).search(r).group(2),
                    'num_recommended': re.compile(p).search(r).group(4)
                    if re.compile(p).search(r).group(4) is not None else None,
                    'num_entered': re.compile(p).search(r).group(6)
                    if re.compile(p).search(r).group(6) is not None else 0,
                    'competition_link': re.compile(p).search(r).group(7)
                    if re.compile(p).search(r).group(6) is not None else None
                }).tolist()))
        table.drop('Конкурс', axis=1, inplace=True)

        return table

    @staticmethod
    def parse_number_of_places(table):
        p = r'(ЛО:\s)(\d+)(ДЗ:\s)?(\d+)?'

        table = table.join(
            pd.DataFrame(
                table['Обсяги'].map(lambda r: {
                    'paid_places': re.compile(p).search(r).group(2)
                    if re.compile(p).search(r) is not None else 0,
                    'free_places': re.compile(p).search(r).group(4)
                    if re.compile(p).search(r) is not None else 0
                }).tolist()))
        table.drop('Обсяги', axis=1, inplace=True)

        return table

    @staticmethod
    def parse_needed_subjects(table):
        subjects = r'[а-яА-ЯїґєіІ\s]*'
        scores = r'\(k=(0\.\d+|0)\)'
        splitter = r'\d\.\s'

        table['required_subj'] = table['Предмети'].astype(str) \
            .map(re.compile(splitter).split) \
            .map(lambda r: [i.strip() for i in r if i != '']) \
            .map(lambda r: [
                {i.replace('або ', '').strip(): re.search(scores, l).group(1)
                 if re.search(scores, l) is not None else "1"
                 for i in re.findall(subjects, l) if i.strip() != ''}
                for l in r]).tolist()
        table['required_subj'] = table['required_subj'] \
            .map(lambda r: [{k: v for k, v in d.items()
                             if k != 'Іноземна мова'} if 'Іноземна мова' in d and len(d) > 1 else d
                            for d in r])

        # splitting by numerators like "1. ", "2. ", "3. "
        # cleaning from '' in lists after splitting
        # generating list of dicts of possible ZNOs

        table.drop('Предмети', axis=1, inplace=True)

        return table

    @staticmethod
    def parse_specialities(table):
        ukr_ = r"а-я А-Я їґєіІ\’\-"
        p = r'(^[{} \s*]+\s?(\([{} \s*\,0-9]+\))?)\,?\s?([{}\, \s*?^]+)?(\,\s?[Ф|ф]акультет:)' \
            .format(ukr_, ukr_, ukr_)
        table = table.join(
            pd.DataFrame(
                table['Спеціальність'].map(lambda r: {
                    'degree': re.compile(p).search(r).group(1)
                    if re.compile(p).search(r) is not None else None,
                    'degree_subname': re.compile(p).search(r).group(3)
                    if re.compile(p).search(r) is not None else None
                }).tolist()))
        p = r'(\,\s?[Ф|ф]акультет:)\s?\,?([а-яА-ЯїґєіІ\’\'\-\" \s*]+)?\,?((.*)?\,)?([а-яА-ЯїґєіІ\’\'\-\,\" \s*]+)?'
        table = table.join(
            pd.DataFrame(
                table['Спеціальність'].map(lambda r: {
                    'faculty': re.compile(p).search(r).group(2)
                    if re.compile(p).search(r) is not None else None,
                    'specialization_1': re.compile(p).search(r).group(4)
                    if re.compile(p).search(r) is not None else
                    re.compile(p).search(r).group(5),
                    'specialization_2': re.compile(p).search(r).group(5)
                    if re.compile(p).search(r) is not None else None
                }).tolist()))

        table.drop('Спеціальність', axis=1, inplace=True)

        return table


class VNZPage(VNZparser):
    def __init__(self):
        self.passed = True
        self.data = pd.DataFrame()
        super(VNZparser).__init__()

    def parse_data(self, link):
        self.link = link
        self.html = requests.get(link).content.decode()
        self.check_data()
        if self.passed:
            den_html, zao_html = self.spliting_data()
            if den_html is not None:
                den_data = self.convert_html_to_df(den_html, 'd')
            else:
                den_data = pd.DataFrame()
            if zao_html is not None:
                zao_data = self.convert_html_to_df(zao_html, 'z')
            else:
                zao_data = pd.DataFrame()
            self.data = den_data.append(zao_data)

    def check_data(self):
        self.html = re.sub('<a.*?href="(.*?)">(.*?)</a>', '\\1 \\2', self.html)
        # checking on tables in html
        try:
            temp = pd.read_html(self.html)
        except ValueError:
            self.passed = False
            return logger.info('No tables found at %s' % self.link)
        try:
            uni_info_table = temp[0]
        except IndexError:
            self.passed = False
            return logger.info('Link %s is broken.' % self.link)
        # checking on basic info about uni
        try:
            uni_info_table = uni_info_table \
                .rename(columns={0: 'data_type',
                                 1: 'uni_info'}) \
                .set_index("data_type")
            uni_info_table.index = uni_info_table.index.map(UNI_INFO_MAPPER.get)
            self.uni_info_table = uni_info_table
            logger.info('Working with "%s"' % uni_info_table.ix['uni_name'].values[0])
        except AttributeError :
            self.passed = False
            return logger.info('Link %s is broken.' % self.link)
        except KeyError:
            self.passed = False
            return logger.info('Link %s is broken.' % self.link)

    def spliting_data(self):
        den_part = [i.start() for i in re.finditer(r'(<!-- den -->)', self.html)]
        zao_part = [i.start() for i in re.finditer(r'(<!-- zao -->)', self.html)]

        try:
            pd.read_html(self.html[den_part[0]:den_part[1]])
            den_html = self.html[den_part[0]:den_part[1]]
        except ValueError:
            logger.info("No data for 'denna' study type.")
            den_html = None
        try:
            pd.read_html(self.html[zao_part[0]: zao_part[1]])
            zao_html = self.html[zao_part[0]: zao_part[1]]
        except ValueError:
            logger.info("No data for 'zaochna' study type.")
            zao_html = None
        return den_html, zao_html

    def convert_html_to_df(self, html_text, data_type):

        final_table = self.combine_data(html_text, data_type)
        final_table = self.parse_number_of_places(final_table)
        final_table = self.parse_students_numbers(final_table)
        final_table = self.parse_needed_subjects(final_table)
        final_table = self.parse_specialities(final_table)

        return final_table

    def get_uni_info(self):
        return self.uni_info_table

    def get_uni_data(self):
        return self.data
