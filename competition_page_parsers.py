import pandas as pd
import re
import requests

COMPETITION_MAPPER = {
    "ПІБ": "student_name",
    "П": "priority",
    "Σ": "student_points",
    "БДО": "school_certificate",
    "ЗНО": "student_zno",
    "ЕКЗ": "enterance_points",
    "ОП": "aditional_points",
    "Д": "original_docs"
}


class CompetitionPage:
    def __init__(self, logger):
        self.logger = logger
        self.passed = True

    def check_link(self):
        self.html = requests.get(self.link).content.decode()
        try:
            p = r"\<table id=\"(\d+)\" class=\"tablesaw tablesaw\-stack"
            self.competition_id = int(re.search(p, self.html).group(1))
        except ValueError:
            self.logger.info("Can't parse competition on %s" % self.link)
            self.passed = False

    def read_dataframe(self):
        try:
            self.table = pd.read_html(self.html, attrs={'id': str(self.competition_id)})[0]
        except TypeError:
            self.logger.info("Can't read table on %s" % self.link)
            self.passed = False
        except IndexError:
            self.logger.info("Something strange is going on in w/ tables %s" % self.link)
            self.passed = False

    def format_dataframe(self):
        self.table.rename(columns=COMPETITION_MAPPER, inplace=True)
        self.table = self.table.ix[:self.table.shape[0] - 2]
        self.table.set_index('#', inplace=True)
        self.table['priority'] = self.table['priority'].replace('—', 0)

    def get_data(self, link):
        self.link = link
        self.check_link()
        self.read_dataframe()
        if self.passed:
            self.format_dataframe()
            return self.table
