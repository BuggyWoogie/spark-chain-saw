import sys
import requests
from bs4 import BeautifulSoup


def main(args):
    if len(args) == 0:
        print("Please provide the url where to find the spark UI (e.g. http://localhost:8080)")
        return 1

    spark_url = args[0]
    ui = requests.get(spark_url)
    soup = BeautifulSoup(ui.text, 'html.parser')

    title = soup.find(id='running-app')
    table = title.parent.table

    header_tr = table.thead.find_all('th')
    header = [x.text.lower().strip() for x in header_tr]
    duration_index = header.index('duration')
    app_id_index = header.index('application id')
    name_index = header.index('name')
    state_index = header.index('state')
    user_index = header.index('user')

    for row in table.tbody.find_all('tr'):
        cells = row.find_all('td')
        app_id = cells[app_id_index].a.text.replace('\n', '')
        app_name = cells[name_index].text.replace('\n', '')
        user = cells[user_index].text.replace('\n', '')
        duration = cells[duration_index].text.replace('\n', '')
        state = cells[state_index].text.replace('\n', '')
        print(app_id+" "+app_name+" "+user+" "+duration+" "+state)


if __name__ == '__main__':
    main(sys.argv[1:])
