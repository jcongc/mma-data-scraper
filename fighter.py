from bs4 import BeautifulSoup
import requests
from typing import List

class FighterData(object):

    def __init__(self) -> None:
        self.url = None
        self.stats_url = None
        self.history_url = None
        self.name = None
        self.soup = None # Creating a beatifulSoup object
        self.stats_soup = None
        self.history_soup = None

        self.stats_resource = None
        self.history_resource = None

    @staticmethod
    def extract_fighter_id(url: str) -> str:
        parts = url.split('/')
        # The index of 'id' in the list plus one gives the index of the fighter id
        fighter_id_index = parts.index('id') + 1
        fighter_id = parts[fighter_id_index]
        return fighter_id

    # Setting url from the fighter id

    def _set_url_from_id(self, fighter_id) -> None:
        self.url = f"espn.com/mma/fighter/_/id/{fighter_id}"
        self.stats_url = f"espn.com/mma/fighter/stats/_/id/{fighter_id}"
        self.history_url = f"espn.com/mma/fighter/history/_/id/{fighter_id}"

    # Setting url from the fighter page

    def _set_url_from_page(self, fighter_page) -> None:
        fighter_id = self.extract_fighter_id(fighter_page)
        self.url = f"{fighter_page}"
        self.stats_url = f"espn.com/mma/fighter/stats/_/id/{fighter_id}"
        self.history_url = f"espn.com/mma/fighter/history/_/id/{fighter_id}"
    
    # Setting resource

    def _set_resource(self):

        # Setting a user-agent to bypass CloudFront 

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        stats_resource = requests.get(f"https://{self.stats_url}", headers=headers)
        history_resource = requests.get(f"https://{self.history_url}", headers=headers)
        self.stats_resource = stats_resource
        self.history_resource = history_resource
        return stats_resource
    
    # Creating beautiful soup object

    def _set_soup(self) -> None:
        self.soup = BeautifulSoup(self.stats_resource.content, features='html.parser')
        self.history_soup = BeautifulSoup(self.history_resource.content, features='html.parser')

    # Getting all the names of opponents

    def get_opponents(self) -> List[str]:
        tbody = self.history_soup.find('tbody', {'class' : 'Table__TBODY'})
        if tbody is not None:
            anchors = tbody.find_all('a', {'class' : 'AnchorLink tl'})
            opponents = [anchor.text for anchor in anchors]
            return opponents
        else:
            return []
        
    # Getting results of previous fights

    def get_results(self) -> List[str]:
        tbody = self.history_soup.find('tbody', {'class' : 'Table__TBODY'})
        if tbody is not None:
            divs = tbody.find_all('div', {'class' : 'ResultCell'})
            results = [div.text for div in divs]
            return results
        else: 
            return []
    
    # Get methods of how a fight ended 

    def get_methods(self) -> List[str]:
        tbody = self.history_soup.find('tbody', {'class' : 'Table__TBODY'})
        if tbody is not None:
            divs = tbody.find_all('div', {'class' : 'FightHistoryCard__Decision tl'})
            methods = [div.text for div in divs]
            return methods
        else:
            return []
        
    # Get round of when a fight ended

    def get_round(self) -> List[str]:
        tbody = self.history_soup.find('tbody', {'class' : 'Table__TBODY'})
        if tbody is not None:
            rows = tbody.find_all('tr')
            round_end = []
            for row in rows:
                tds = row.find_all('td', {'class' : 'Table__TD'})
                round_number = tds[-3].text
                round_end.append((round_number))
            return round_end
        else:
            return []

    # Get the time of the round when the fight ended

    def get_time(self) -> List[str]:
        tbody = self.history_soup.find('tbody', {'class' : 'Table__TBODY'})
        if tbody is not None:
            rows = tbody.find_all('tr')
            time = []
            for row in rows:
                tds = row.find_all('td', {'class' : 'Table__TD'})
                end_time = tds[-2].text
                time.append((end_time))
            return time
        else:
            return []
    
    # Get the event which the fighter fought

    def get_event(self) -> List[str]:
        tbody = self.history_soup.find('tbody', {'class' : 'Table__TBODY'})
        if tbody is not None:
            rows = tbody.find_all('tr')
            events = []
            for row in rows:
                tds = row.find_all('td', {'class' : 'Table__TD'})
                event = tds[-1].text
                events.append((event))
            return events
        else:
            return []
        
    # Get record of the fighter, including their finish record
    
    def get_record(self) -> List[str]:
        records = self.history_soup.find_all('div', {'class' : 'StatBlockInner__Value tc fw-medium n2 clr-gray-02'}, limit=3)
        record_texts = []
        if records:
            for record in records:
                record_texts.append(record.text)
        return record_texts
    
    # Get the name of the fighter

    def get_name(self) -> str:
        fighter_name_element = self.history_soup.find('h1', {'class': 'PlayerHeader__Name flex flex-column ttu fw-bold pr4 h2'})
        if fighter_name_element is not None:
            fighter_name = ' '.join(child.get_text() for child in fighter_name_element.children)
        else:
            fighter_name = 'Fighter Name Not Found'
        return fighter_name

    # Get the striking stats of a fighter

    def get_striking(self) -> tuple[List[str], List[List[str]]]:
        tbody = self.soup.find_all('tbody', {'class' : 'Table__TBODY'})
        striking_stats = []
        striking_table = tbody[0]
        table_row = striking_table.find_all('tr', {'class' : 'Table__TR Table__TR--sm Table__even'})
        table_headings = self.soup.find_all('tr', {'class': 'Table__TR Table__even'})
        table_heading = table_headings[0].find_all('th', {'class': 'Table__TH'})
        headings = []
        for index, heading in enumerate(table_heading):
            if index >= 4:
                headings.append(heading.text.strip())
        for row in table_row:
            stat_row = []
            stat_value = row.find_all('td', {'class' : 'tar Table__TD'})
            for stat in stat_value:
                stat_row.append(stat.text)
            striking_stats.append(stat_row)
        return headings, striking_stats
    
    # Finds the average of a column

    def find_column_avg(self, stats: List[List[str]]) -> List[float]:
        num_row = len(stats[0])
        col_sums = [0.0] * num_row
        col_counts = [0] * num_row
        for row in stats:
            for i, value in enumerate(row):
                if value == '-': # Case where the stat is -
                    continue
                elif '/' in value:
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

        column_avg = [col_sums[i] / col_counts[i] if col_counts[i] != 0 else 0 for i in range(num_row)]
        return column_avg
    
    # Get the clinch stats of a fighter

    def get_clinch(self) -> tuple[List[str], List[List[str]]]:
        tbody = self.soup.find_all('tbody', {'class': 'Table__TBODY'})
        clinch_stats = []
        clinch_table = tbody[1] 
        table_row = clinch_table.find_all('tr', {'class': 'Table__TR Table__TR--sm Table__even'})
        table_headings = self.soup.find_all('tr', {'class': 'Table__TR Table__even'})
        table_heading = table_headings[1].find_all('th', {'class': 'Table__TH'})
        
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

    # Get the ground stats of a fighter
    
    def get_ground(self) -> tuple[List[str], List[List[str]]]:
        tbody = self.soup.find_all('tbody', {'class': 'Table__TBODY'})
        ground_stats = []
        ground_table = tbody[2]
        table_row = ground_table.find_all('tr', {'class': 'Table__TR Table__TR--sm Table__even'})
        table_headings = self.soup.find_all('tr', {'class': 'Table__TR Table__even'})
        table_heading = table_headings[2].find_all('th', {'class': 'Table__TH'})
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