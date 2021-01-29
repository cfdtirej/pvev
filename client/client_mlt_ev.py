import time
from datetime import datetime
from pathlib import Path
import requests
import yaml
import pandas as pd


meshcode = {
    'north': 543771363,
    'east': 543771054,
    'west': 543761864,
    'south': 543771291,
}


def ev_stat_itor() -> dict:
    for ts in pd.date_range(start='2020-08-02 00:00:00', end='2020-08-02 23:30:00', freq='min'):
        ts = datetime.strptime(str(ts), '%Y-%m-%d %H:%M:%S')
        post_json = {
            'time': ts.isoformat().replace('T', ' '),
            'EV_stat': [
                {
                    'CarID': 1.111,
                    'charge': 1,
                    'meshcode': meshcode['north'] if (ts > datetime(2020, 8, 2, 10, 10, 00)) and (ts < datetime(2020, 8, 2, 10, 10, 00)) else 11111,
                    'latitude': 12.2,
                    'longitude': 34.4
                },
                {
                    'CarID': 2,
                    'charge': 0,
                    'meshcode': meshcode['east'],
                    'latitude': 5.4,
                    'longitude': 4.4
                },
                {
                    'CarID': 3,
                    'charge': 1000,
                    'meshcode': meshcode['south'] if (ts > datetime(2020, 8, 2, 2, 0, 0)) and (ts < datetime(2020, 8, 2, 4, 0, 0)) else 3333,
                    'latitude': 12.2,
                    'longitude': 34.4
                },
                {
                    'CarID': 4,
                    'charge': 1.4444,
                    'meshcode': meshcode['north'] if (ts > datetime(2020, 8, 2, 10, 16, 00)) and (ts < datetime(2020, 8, 2, 10, 26, 00)) else 44444,
                    'latitude': 5.4,
                    'longitude': 4.4
                }
            ]
        }
        yield post_json


for data in ev_stat_itor():
    print(data)
    res = requests.post(url=f'http://localhost:50001/', json=data)
    print(res.json())
    print()
    time.sleep(0.05)
