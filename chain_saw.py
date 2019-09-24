import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sys


def kill_app(app_id, spark_url):
    params = {'id': app_id, 'terminate': 'true'}
    requests.post(spark_url+'/app/kill/', params=params)


def duration_in_hours(duration):
    raw_duration=duration.lower().strip()
    if not raw_duration.endswith('h'):
        return 0
    hours = re.compile('\s+').split(raw_duration)[0]
    return float(hours)


def main(args):
    if len(args) == 0:
        print("Please provide the url where to find the spark UI (e.g. http://localhost:8080)")
        return 1
    spark_url = args[0]
    running_msg = '[{}] Running the chain saw on {}'
    now = str(datetime.now())
    print(running_msg.format(now, spark_url))

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
        state = cells[state_index].text.lower()
        now = str(datetime.now())
        duration_in_h = duration_in_hours(duration)
        # TODO: make the 12h and 48h threshold configurable
        if state.find('running') >= 0 and duration_in_h > 12:
            kill_app(app_id, spark_url)
            msg = '[{}] Killing app {} (id={}) of user {} that has been running for {}'
            print(msg.format(now, app_name, app_id, user, duration))
        if state.find('waiting') >= 0 and duration_in_h > 48:
            kill_app(app_id, spark_url)
            msg = '[{}] Killing app {} (id={}) of user {} that has been waiting for {}'
            print(msg.format(now, app_name, app_id, user, duration))
    return 0


if __name__ == '__main__':
    main(sys.argv[1:])
