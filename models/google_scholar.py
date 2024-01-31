import logging

import requests
from bs4 import SoupStrainer, BeautifulSoup
from pydantic import BaseModel
from requests import Response

logger = logging.getLogger(__name__)


class GoogleScholarSearch(BaseModel):
    search_string: str

    def in_title_url(self, lang: str = "en"):
        """Replace spaces with '+'
        We use the danish version because it is easier to parse :)
        https://scholar.google.com/scholar?as_q=&as_epq=love&as_oq=&as_eq=&as_occt=title&as_sauthors=&as_publication=&as_ylo=&as_yhi=&hl=da&as_sdt=0%2C5&as_vis=1"""
        return f"https://scholar.google.com/scholar?as_q=&hl={lang}&as_epq={self.search_string.replace(' ', '+')}&as_occt=titleas_sdt=0%2C5&as_vis=1"

    def everywhere_url(self, lang: str = "en"):
        """Replace spaces with '+'"""
        return f"https://scholar.google.com/scholar?hl={lang}&q=%22{self.search_string.replace(' ', '+')}%22"

    @staticmethod
    def parse_response(response: Response) -> int:
        # html_content = '<div class="gs_ab_mdw">Ca. 3.690.000 resultater (<b>0,13</b> sek.)</div>'
        only_div_with_class = SoupStrainer('div', class_='gs_ab_mdw')
        soup = BeautifulSoup(response.text, 'lxml', parse_only=only_div_with_class)
        result_text = soup.get_text(strip=True)
        # logger.debug(result_text)
        # Extracting "3.690.000" based on spaces
        numbers = result_text.split()
        total = int(numbers[1].replace(".", "")) if len(numbers) > 1 else 0
        return total

    @property
    def everywhere_total_results(self) -> int:
        # logger.debug("getting total results from google")
        response = requests.get(self.everywhere_url(lang="da"))
        if response.status_code == 200:
            total = self.parse_response(response=response)
            logger.debug(f"gs everywhere total: {total}")
            return total

    @property
    def in_title_total_results(self) -> int:
        # logger.debug("getting total results from google")
        response = requests.get(self.in_title_url(lang="da"))
        if response.status_code == 200:
            total = self.parse_response(response=response)
            logger.debug(f"gs in title total: {total}")
            return total
