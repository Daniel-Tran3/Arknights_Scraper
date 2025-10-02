import requests
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd

URL = "https://arknights.wiki.gg/wiki/Event/Upcoming"

CN_EN_OFFSET = 166
EVENT_TYPES = ["Side Story", "Intermezzo"]

def main():
    r = requests.get(URL)


    soup = BeautifulSoup(r.content, 'html.parser')

    # To figure out what the class of table is that we want
    # Compare with Inspect Element
    #for table in soup.find_all('table'):
    #    print(table.get('class'))

    event_table = soup.find('table', class_='mrfz-wtable flex-table')

    event_list = []

    for row in event_table.tbody.find_all('tr'):
        columns = row.find_all('td')
        if (columns != []):
            event = columns[0].text.strip()
            release_date = columns[1].text.strip()
            if (release_date.count('/') >= 4 and any(elem in event for elem in EVENT_TYPES)):
                CN_date = re.search(r'CN: ..../../..–..../../..', release_date).group()
                CN_num_date = CN_date.split(" ")[1]
                CN_start = CN_num_date.split("–")[0]
                CN_end = CN_num_date.split("–")[1]
                CN_start_dt = datetime.datetime.strptime(CN_start, "%Y/%m/%d")
                CN_end_dt = datetime.datetime.strptime(CN_end, "%Y/%m/%d")
                EN_start = CN_start_dt + datetime.timedelta(days=CN_EN_OFFSET)
                EN_end = CN_end_dt + datetime.timedelta(days=CN_EN_OFFSET)

                event_list.append([event, EN_start, EN_end])
    event_df = pd.DataFrame(event_list, columns=["Event", "Start", "End"])
    print(event_df)
    return event_list

if __name__ == "__main__":
    main()
