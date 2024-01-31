import logging

import requests
from bs4 import SoupStrainer, BeautifulSoup
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class GoogleScholarSearch(BaseModel):
    search_string: str

    def da_url(self):
        """Replace spaces with '+'
        We use the danish version because it is easier to parse :)"""
        return f"https://scholar.google.com/scholar?hl=da&q=%22{self.search_string.replace(' ', '+')}%22"

    def en_url(self):
        """Replace spaces with '+'"""
        return f"https://scholar.google.com/scholar?hl=en&q=%22{self.search_string.replace(' ', '+')}%22"

    def total_results(self) -> int:
        # logger.debug("getting total results from google")
        response = requests.get(self.da_url())
        if response.status_code == 200:
            # print("200")
            from lxml import html
            # html_content = '<div class="gs_ab_mdw">Ca. 3.690.000 resultater (<b>0,13</b> sek.)</div>'
            # Use SoupStrainer to parse only the relevant part of the HTML
            only_div_with_class = SoupStrainer('div', class_='gs_ab_mdw')
            # Parse the HTML using BeautifulSoup and SoupStrainer
            soup = BeautifulSoup(response.text, 'lxml', parse_only=only_div_with_class)
            # Extract the text from the parsed HTML
            result_text = soup.get_text(strip=True)
            # logger.debug(result_text)
            # Extracting "3.690.000" based on spaces
            numbers = result_text.split()
            total = int(numbers[1].replace(".", "")) if len(numbers) > 1 else 0
            # logger.debug(f"gs total: {total}")
            return total
