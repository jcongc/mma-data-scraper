"""
    Fighter Data Module

    This module provides classes and functions to extract and process data about fighters.
    It includes tools to retrieve fighter information, stats, and history from web pages.
"""

from typing import List
from bs4 import BeautifulSoup
import requests


class FighterData:
    """
        Represents a fighter's data, providing methods to extract and process information.

        Attributes:
            stats_url (str): The URL of the fighter's stats page.
            history_url (str): The URL of the fighter's history page.
            name (str): The name of the fighter.
            soup (BeautifulSoup): The BeautifulSoup object for the fighter's page.
            history_soup (BeautifulSoup): The BeautifulSoup object for the fighter's history page.
            stats_resource (object): The resource object for the fighter's stats.
            history_resource (object): The resource object for the fighter's history.
    """

    def __init__(self) -> None:
        """Initializes a new instance of the class."""
        self.stats_url = None
        self.history_url = None
        self.name = None
        self.soup = None  # Creating a beatifulSoup object
        self.history_soup = None
        self.stats_resource = None
        self.history_resource = None

    @staticmethod
    def extract_fighter_id(url: str) -> str:
        """Extract the fighter id from a given ESPN URL"""
        parts = url.split('/')
        # The index of 'id' in the list plus one gives the index of the fighter
        # id
        fighter_id_index = parts.index('id') + 1
        fighter_id = parts[fighter_id_index]
        return fighter_id

    def set_url_from_id(self, fighter_id) -> None:
        """Sets the URLs after taking in a fighter ID"""
        self.stats_url = f"espn.com/mma/fighter/stats/_/id/{fighter_id}"
        self.history_url = f"espn.com/mma/fighter/history/_/id/{fighter_id}"

    def set_url_from_page(self, fighter_page) -> None:
        """Takes in a URL and sets the URLs of the fighter"""
        fighter_id = self.extract_fighter_id(fighter_page)
        self.stats_url = f"espn.com/mma/fighter/stats/_/id/{fighter_id}"
        self.history_url = f"espn.com/mma/fighter/history/_/id/{fighter_id}"

    def set_resource(self):
        """
            Sets the resources for the fighter's stats by sending HTTP requests.
            Uses a User-Agent as the header.
        """

        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        stats_resource = requests.get(
            f"https://{self.stats_url}", headers=headers, timeout=10)
        history_resource = requests.get(
            f"https://{self.history_url}", headers=headers, timeout=10)
        self.stats_resource = stats_resource
        self.history_resource = history_resource
        return stats_resource

    def set_soup(self) -> None:
        """Sets the soup object from BS"""
        self.soup = BeautifulSoup(
            self.stats_resource.content,
            features='html.parser')
        self.history_soup = BeautifulSoup(
            self.history_resource.content,
            features='html.parser')

    def get_opponents(self) -> List[str]:
        """Gets the opponents which the fighter has fought"""
        tbody = self.history_soup.find('tbody', {'class': 'Table__TBODY'})
        if tbody is not None:
            anchors = tbody.find_all('a', {'class': 'AnchorLink tl'})
            opponents = [anchor.text for anchor in anchors]
            return opponents
        return []

    def get_results(self) -> List[str]:
        """Gets the result of the fight, either a W, L, D or NC"""
        tbody = self.history_soup.find('tbody', {'class': 'Table__TBODY'})
        if tbody is not None:
            divs = tbody.find_all('div', {'class': 'ResultCell'})
            results = [div.text for div in divs]
            return results
        return []

    def get_methods(self) -> List[str]:
        """Gets the method how the fight ended"""
        tbody = self.history_soup.find('tbody', {'class': 'Table__TBODY'})
        if tbody is not None:
            divs = tbody.find_all('div',
                                  {'class': 'FightHistoryCard__Decision tl'})
            methods = [div.text for div in divs]
            return methods
        return []

    def get_round(self) -> List[str]:
        """Gets the round which the fight ended"""
        tbody = self.history_soup.find('tbody', {'class': 'Table__TBODY'})
        if tbody is not None:
            rows = tbody.find_all('tr')
            round_end = []
            for row in rows:
                tds = row.find_all('td', {'class': 'Table__TD'})
                round_number = tds[-3].text
                round_end.append((round_number))
            return round_end
        return []

    def get_time(self) -> List[str]:
        """Gets the time in the round which it ended"""
        tbody = self.history_soup.find('tbody', {'class': 'Table__TBODY'})
        if tbody is not None:
            rows = tbody.find_all('tr')
            time = []
            for row in rows:
                tds = row.find_all('td', {'class': 'Table__TD'})
                end_time = tds[-2].text
                time.append((end_time))
            return time
        return []

    def get_event(self) -> List[str]:
        """Gets the event that a fighter fought at"""
        tbody = self.history_soup.find('tbody', {'class': 'Table__TBODY'})
        if tbody is not None:
            rows = tbody.find_all('tr')
            events = []
            for row in rows:
                tds = row.find_all('td', {'class': 'Table__TD'})
                event = tds[-1].text
                events.append((event))
            return events
        return []

    def get_record(self) -> List[str]:
        """Gets a fighter's record in the formal W-L-D"""
        records = self.history_soup.find_all(
            'div', {'class': 'StatBlockInner__Value tc fw-medium n2 clr-gray-02'}, limit=3)
        record_texts = []
        if records:
            for record in records:
                record_texts.append(record.text)
        return record_texts

    def get_name(self) -> str:
        """Gets the name of a fighter after taking in their ID"""
        fighter_name_element = self.history_soup.find(
            'h1', {'class': 'PlayerHeader__Name flex flex-column ttu fw-bold pr4 h2'})
        if fighter_name_element is not None:
            fighter_name = ' '.join(child.get_text()
                                    for child in fighter_name_element.children)
        else:
            fighter_name = 'Fighter Name Not Found'
        return fighter_name

    def get_striking(self) -> tuple[List[str], List[List[str]]]:
        """Gets the striking statistics of a fighter"""
        tbody = self.soup.find_all('tbody', {'class': 'Table__TBODY'})
        striking_stats = []
        striking_table = tbody[0]
        table_row = striking_table.find_all(
            'tr', {'class': 'Table__TR Table__TR--sm Table__even'})
        table_headings = self.soup.find_all(
            'tr', {'class': 'Table__TR Table__even'})
        table_heading = table_headings[0].find_all(
            'th', {'class': 'Table__TH'})
        headings = []
        for index, heading in enumerate(table_heading):
            if index >= 4:
                headings.append(heading.text.strip())
        for row in table_row:
            stat_row = []
            stat_value = row.find_all('td', {'class': 'tar Table__TD'})
            for stat in stat_value:
                stat_row.append(stat.text)
            striking_stats.append(stat_row)
        return headings, striking_stats

    def get_clinch(self) -> tuple[List[str], List[List[str]]]:
        """Gets the clinch statistics of a fighter"""
        tbody = self.soup.find_all('tbody', {'class': 'Table__TBODY'})
        clinch_stats = []
        clinch_table = tbody[1]
        table_row = clinch_table.find_all(
            'tr', {'class': 'Table__TR Table__TR--sm Table__even'})
        table_headings = self.soup.find_all(
            'tr', {'class': 'Table__TR Table__even'})
        table_heading = table_headings[1].find_all(
            'th', {'class': 'Table__TH'})

        headings = []
        for index, heading in enumerate(table_heading):
            if index >= 4:
                headings.append(heading.text.strip())

        for row in table_row:
            stat_row = []
            stat_value = row.find_all('td', {'class': 'tar Table__TD'})
            for stat in stat_value:
                stat_row.append(stat.text)
            clinch_stats.append(stat_row)

        return headings, clinch_stats

    def get_ground(self) -> tuple[List[str], List[List[str]]]:
        """Gets the ground statistics of a fighter"""
        tbody = self.soup.find_all('tbody', {'class': 'Table__TBODY'})
        ground_stats = []
        ground_table = tbody[2]
        table_row = ground_table.find_all(
            'tr', {'class': 'Table__TR Table__TR--sm Table__even'})
        table_headings = self.soup.find_all(
            'tr', {'class': 'Table__TR Table__even'})
        table_heading = table_headings[2].find_all(
            'th', {'class': 'Table__TH'})
        headings = []
        for index, heading in enumerate(table_heading):
            if index >= 4:
                headings.append(heading.text.strip())
        for row in table_row:
            stat_row = []
            stat_value = row.find_all('td', {'class': 'tar Table__TD'})
            for stat in stat_value:
                stat_row.append(stat.text)
            ground_stats.append(stat_row)
        return headings, ground_stats

    def find_column_avg(self, stats: List[List[str]]) -> List[float]:
        """Finds the average of a column in the statistics table"""
        num_row = len(stats[0])
        col_sums = [0.0] * num_row
        col_counts = [0] * num_row
        for row in stats:
            for i, value in enumerate(row):
                if value == '-':  # Case where the stat is -
                    continue
                if '/' in value:
                    numeric_value = float(value.split('/')[0])
                    col_sums[i] += numeric_value
                    col_counts[i] += 1
                elif '%' in value:
                    numeric_value = float(value.strip('%'))
                    col_sums[i] += numeric_value
                    col_counts[i] += 1
                else:
                    numeric_value = float(value)
                    col_sums[i] += numeric_value
                    col_counts[i] += 1

        column_avg = [col_sums[i] / col_counts[i]
                      if col_counts[i] != 0 else 0 for i in range(num_row)]
        return column_avg
