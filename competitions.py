import logging.config
import pandas as pd
import re
import requests

logging.config.fileConfig('./logging.conf')

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
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.table_passed = True
        self.link_passed = True

    def check_link(self, link):
        self.html = requests.get(link).content.decode()
        try:
            p = r"\<table id=\"(\d+)\" class=\"tablesaw tablesaw\-stack"
            self.competition_id = int(re.search(p, self.html).group(1))
        except Exception as e:
            self.logger.warning("Can't get competition id %s" % link)
            self.logger.info("Failed with error %s" % e)
            self.link_passed = False

    def read_dataframe(self):
        try:
            self.table = pd.read_html(self.html,
                                      attrs={'id': str(self.competition_id)},
                                      flavor='html5lib')[0]
        except Exception as e:
            self.logger.warning("Can't read table. Failed with error : %s" % e)
            self.table_passed = False

    def format_dataframe(self):
        self.table.rename(columns=COMPETITION_MAPPER, inplace=True)
        self.table = self.table.ix[:self.table.shape[0] - 2]
        self.table.set_index('#', inplace=True)
        if "priority" not in self.table.columns:
            self.table['priority'] = None
        else:
            self.table['priority'] = self.table['priority'].replace('—', 0)
            self.table['priority'] = self.table['priority'].astype(int)

    def get_data(self, link):
        self.check_link(link)
        if self.link_passed:
            self.read_dataframe()
        if self.table_passed:
            self.format_dataframe()
            return self.table
        return pd.DataFrame()
