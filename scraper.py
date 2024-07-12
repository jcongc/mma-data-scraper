from bs4 import BeautifulSoup
import requests
from typing import List
import re
from prettytable import PrettyTable

# An instance of a fighter and their corresponding data

class FighterData(object):

    def __init__(self) -> None:
        self.url = None
        self.stats_url = None
        self.history_url = None
        self.name = None
        self.soup = None # Creating a beatifulSoup object
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

def main() -> None:
    # Create an instance of the FighterData class
    fighter = FighterData()

    # Ask the user for a fighter id or their ESPN URL
    user_input = input("Please enter a fighter id or their ESPN URL: ")

    # Check if the user input is a fighter id or an ESPN URL
    if re.match(r'^\d+$', user_input):  # If the user input is a fighter id
        fighter._set_url_from_id(user_input)
    elif re.match(r'^(https?://(www.)?)?espn\.com/mma/fighter/_/id/\d+(/[\w-]+)?$', user_input):  # If the user input is an ESPN URL
        fighter._set_url_from_page(user_input)
    else:
        print("Invalid input. Please enter a fighter id or an ESPN URL.")
        return

    # Set the resource
    
    fighter._set_resource()

    # Set the soup object
    
    fighter._set_soup()

    # Get the opponents
    
    opponents = fighter.get_opponents()

    # Get the results
    
    results = fighter.get_results()

    # Get the method a fight ended
    
    methods = fighter.get_methods()

    # Get the round the fight ended
    
    end_round = fighter.get_round()

    # Get the the time which a fight ended

    time = fighter.get_time()

    # Get the event which the fighter fought at

    event = fighter.get_event()

    records = fighter.get_record()

    fighter_name = fighter.get_name()

    print(fighter_name)
    print(f"Record: {records[0]}")
    print(f"TKO/KO: {records[1]}")
    print(f"Submissions: {records[2]}")
    
    # Create a table with all the results

    table = PrettyTable()

    table.field_names = ["Opponent", "Result", "Method", "Round", "Time", "Event"]

    for opponent, result, method, end_round, time, event in zip(opponents, results, methods, end_round, time, event):
        table.add_row([opponent, result, method, end_round, time, event])
    
    print(table)

if __name__ == "__main__":
    main()