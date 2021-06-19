import requests
from bs4 import BeautifulSoup as Bf
import logging



logger = logging.getLogger("utils")

class GetAllCountryData:
    def __init__(self):
        self.receive = requests.get('https://www.worldometers.info/coronavirus/#countries')
        self.html = self.receive.text
        self.soup = Bf(self.html, 'html.parser')
        self.table = self.soup.find_all(class_='mt_a')
        self.class_name='GetAllCountryData'
        self.database = {}



    def get_data(self):

        if self.receive.status_code != 200:
            return self.receive.status_code, "Please try again later"
        else:
            for tr in self.table:
                parent_node = tr.parent.parent
                rows =[]
                for node in parent_node:
                    try:
                        rows.append(" ".join(node.text.split()))
                    except Exception as e:
                        logger.info(e)

                        pass
                self.database[rows[1].lower()] = {
                                                "Total Case":rows[2],
                                                "New Cases": rows[3],
                                                "Total Deaths":rows[4],
                                                "Total Recovered":rows[6],
                                                "Total Active": rows[8],
                                                "Population": rows[14]
                                                }
            return self.receive.status_code, self.database.get(self.country_name)






