import csv
import json
import socket
import time
import os
import bz2
import glob

from multiprocessing import Process
from datetime import datetime
from typing import List, Dict

import yaml


def field_type_conv(csv_file: str) -> list:
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        fields = []
        for row in reader:
            line = []
            for v in row:
                try:
                    value = float(v)
                except ValueError:
                    value = str(v)
                line.append(value)
            fields.append(line)
    del fields[0]
    return fields


def to_rfc3339(timestamp: str) -> str:
    if '/' in timestamp:
        return datetime.strptime(timestamp.partition('.')[0] + '+0900', '%Y/%m/%d %H:%M:%S%z').isoformat()
    elif '-' in timestamp:
        return datetime.strptime(timestamp.partition('.')[0] + '+0900', '%Y-%m-%d %H:%M:%S%z').isoformat()


def some_TScsv_to_dict(csv_list: List[str]) -> dict:
    result = {}
    for csvfile in csv_list:
        with open(csvfile) as f:
            table = [[i[0], float(i[1]) if float(i[1]) else i[1]]
                     for i in csv.reader(f)]
            header = table.pop(0)
            result[str(int(header[1]))] = table
    return result


class CreateDataFields:

    def create_data_fields(self, pd_csv_list: List[str], ppv_csv_list: List[str]):
        self.idx = 0
        self.pd_fields = some_TScsv_to_dict(pd_csv_list)
        self.ppv_fields = some_TScsv_to_dict(ppv_csv_list)
        keys = list({_ for _ in list(self.pd_fields.keys()) +
                     list(self.ppv_fields.keys())})
        # self.data_fields is 30-minutes interval data
        """
        {
            meshcode: {
                "pd": [two-dementional list of pd],
                "ppv" [two-dementional list of ppv]
            },...
        }
        """
        self.data_fields = {k: {'pd': self.pd_fields[k], 'ppv': self.ppv_fields[k]}
                            for k in keys}

    def get_pd_fields(self) -> dict:
        return self.pd_fields

    def get_ppv_fields(self) -> dict:
        return self.pd_fields

    def get_data_fields(self) -> dict:
        return self.data_fields


class ChargerDataServerAndClient:
    def __init__(self, client_host: str, client_port: int, server_host: str, server_port: int):
        self.client_host = client_host
        self.client_port = client_port
        self.server_host = server_host
        self.server_port = server_port
        self.idx = 0

    def send_recv_data(self, pd_csv_list: List[str], ppv_csv_list: List[str]) -> None:
        create_data = CreateDataFields(pd_csv_list, ppv_csv_list)
        data_fields = create_data.data_fields
        idx_030, idx_060, idx_090, idx_120, idx_150, idx_180 = 1, 2, 3, 4, 5, 6
        pd_add = 0
        flag = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.server_host, self.server_port))
            server.listen()
            while flag:
                conn, addr = server.accept()
                with conn:
                    while flag:
                        resv_data = conn.recv(1024)
                        print(type(resv_data))
                        data_json = json.loads(resv_data.decode())
                        pd_add += data_json['charge']
                        record_minute = datetime.strptime(
                            data_json['time'], '%Y/%m/%d %H:%M:%S').minute
                        if (record_minute == 0) or (record_minute == 30):
                            if idx_030 >= 48:
                                idx_030 = 0
                            elif idx_060 >= 48:
                                idx_060 = 0
                            elif idx_090 >= 48:
                                idx_090 = 0
                            elif idx_120 >= 48:
                                idx_120 = 0
                            elif idx_150 >= 48:
                                idx_150 = 0
                            elif idx_180 >= 48:
                                idx_180 = 0
                            meshcode = data_json['meshcode']
                            json_body = {
                                "meshcode": meshcode,
                                "time": data_fields[str(meshcode)]['pd'][self.idx][0],
                                "pd": data_fields[str(meshcode)]['pd'][self.idx][1] + pd_add,
                                "pd_030": data_fields[str(meshcode)]['pd'][idx_030][1],
                                "pd_060": data_fields[str(meshcode)]['pd'][idx_060][1],
                                "pd_090": data_fields[str(meshcode)]['pd'][idx_090][1],
                                "pd_120": data_fields[str(meshcode)]['pd'][idx_120][1],
                                "pd_150": data_fields[str(meshcode)]['pd'][idx_150][1],
                                "pd_180": data_fields[str(meshcode)]['pd'][idx_180][1],
                                "ppv": data_fields[str(meshcode)]['ppv'][self.idx][1],
                                "ppv_030": data_fields[str(meshcode)]['ppv'][idx_030][1],
                                "ppv_060": data_fields[str(meshcode)]['ppv'][idx_060][1],
                                "ppv_090": data_fields[str(meshcode)]['ppv'][idx_090][1],
                                "ppv_120": data_fields[str(meshcode)]['ppv'][idx_120][1],
                                "ppv_150": data_fields[str(meshcode)]['ppv'][idx_150][1],
                                "ppv_180": data_fields[str(meshcode)]['ppv'][idx_180][1],
                            }
                            # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                            #     client.connect((self.client_host, self.client_port))
                            #     client.sendall(json.dumps(json_body).encode('utf-8'))
                            #     print(repr(client.recv(1024)))

                            self.idx += 1
                            idx_030 += 1
                            idx_060 += 1
                            idx_090 += 1
                            idx_120 += 1
                            idx_150 += 1
                            idx_180 += 1
                            pd_add = 0

                            print(json_body)
                            conn.sendall(b'Received and Send')
                        else:
                            conn.sendall(b'Received')
                            continue

        if self.idx == len(data_fields[str(meshcode)]['pd']) - 1:
            server.close()
            flag = False


class ChargerDataClient:

    def __init__(self, client_host: str, client_port: int) -> None:
        self.client_host = client_host
        self.client_port = client_port

    def send_first_sample_data(self, meshcode: int, pd_csv: str, ppv_csv: str) -> None:
        pd_fields = field_type_conv(pd_csv)
        ppv_fields = field_type_conv(ppv_csv)
        len_fields = len(pd_fields)
        idx_030, idx_060, idx_090, idx_120, idx_150, idx_180 = 1, 2, 3, 4, 5, 6
        flag = True
        while flag:
            for idx in range(len_fields):
                if idx_030 >= 48:
                    idx_030 = 0
                if idx_060 >= 48:
                    idx_060 = 0
                if idx_090 >= 48:
                    idx_090 = 0
                if idx_120 >= 48:
                    idx_120 = 0
                if idx_150 >= 48:
                    idx_150 = 0
                if idx_180 >= 48:
                    idx_180 = 0
                json_body = {
                    "meshcode": meshcode,
                    "time": to_rfc3339(pd_fields[idx][0]),
                    "pd": pd_fields[idx][1],
                    "pd_030": pd_fields[idx_030][1],
                    "pd_060": pd_fields[idx_060][1],
                    "pd_090": pd_fields[idx_090][1],
                    "pd_120": pd_fields[idx_120][1],
                    "pd_150": pd_fields[idx_150][1],
                    "pd_180": pd_fields[idx_180][1],
                    "ppv": ppv_fields[idx][1],
                    "ppv_030": ppv_fields[idx_030][1],
                    "ppv_060": ppv_fields[idx_060][1],
                    "ppv_090": ppv_fields[idx_090][1],
                    "ppv_120": ppv_fields[idx_120][1],
                    "ppv_150": ppv_fields[idx_150][1],
                    "ppv_180": ppv_fields[idx_180][1],
                }
                print(json_body)
                idx_030 += 1
                idx_060 += 1
                idx_090 += 1
                idx_120 += 1
                idx_150 += 1
                idx_180 += 1
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.connect((self.client_host, self.client_port))
                    client.sendall(json.dumps(json_body).encode('utf-8'))
                    print(repr(client.recv(1024)))
                if idx == len_fields - 1:
                    flag = False

    def send_pd_add_ev_data(self, meshcode: int, pd_csv: str, ppv_csv: str, ev_csv: str) -> None:
        pd_fields = field_type_conv(pd_csv)
        ppv_fields = field_type_conv(ppv_csv)
        ev_field = [[i[0], i[-1]] for i in field_type_conv(ev_csv)]
        len_fields = len(pd_fields)
        idx_030, idx_060, idx_090, idx_120, idx_150, idx_180 = 1, 2, 3, 4, 5, 6
        idx, ev_idx = 0
        pd_add = 0
        flag = True
        while flag:
            pd_add += ev_field[ev_idx][1]
            record_minute = datetime.strptime(
                ev_field[ev_idx][0], '%Y/%m/%d %H:%M:%S').minute
            ev_idx += 1
            if (record_minute == 0) or (record_minute == 30):
                if idx_030 >= 48:
                    idx_030 = 0
                elif idx_060 >= 48:
                    idx_060 = 0
                elif idx_090 >= 48:
                    idx_090 = 0
                elif idx_120 >= 48:
                    idx_120 = 0
                elif idx_150 >= 48:
                    idx_150 = 0
                elif idx_180 >= 48:
                    idx_180 = 0
                json_body = {
                    "meshcode": meshcode,
                    "time": to_rfc3339(pd_fields[idx][0]),
                    "pd": pd_fields[idx][1] + pd_add,
                    "pd_030": pd_fields[idx_030][1],
                    "pd_060": pd_fields[idx_060][1],
                    "pd_090": pd_fields[idx_090][1],
                    "pd_120": pd_fields[idx_120][1],
                    "pd_150": pd_fields[idx_150][1],
                    "pd_180": pd_fields[idx_180][1],
                    "ppv": ppv_fields[idx][1],
                    "ppv_030": ppv_fields[idx_030][1],
                    "ppv_060": ppv_fields[idx_060][1],
                    "ppv_090": ppv_fields[idx_090][1],
                    "ppv_120": ppv_fields[idx_120][1],
                    "ppv_150": ppv_fields[idx_150][1],
                    "ppv_180": ppv_fields[idx_180][1],
                }

                # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                #     client.connect((self.client_host, self.client_port))
                #     client.sendall(json.dumps(json_body).encode('utf-8'))
                #     print(repr(client.recv(1024)))

                pd_add = 0
                idx += 1
                idx_030 += 1
                idx_060 += 1
                idx_090 += 1
                idx_120 += 1
                idx_150 += 1
                idx_180 += 1
                print(json_body)

            if idx == len_fields - 1:
                flag = False


if __name__ == '__main__':
    from pprint import pprint
    yaml_config = os.path.join(os.path.dirname(__file__), 'config/config.yaml')
    with open(yaml_config, 'r') as yf:
        config = yaml.safe_load(yf)
        client_host = config["SocketClient"]["host"]
        client_port = config["SocketClient"]["port"]
    pwd = os.path.dirname(__file__)
    pdcsv = os.path.join(pwd, 'data/pd/pd_sample.csv')
    ppvcsv = os.path.join(pwd, 'data/ppv/ppv_sample.csv')
    evcsv = os.path.join(pwd, 'data/ev/ev_sample.csv')
    pd_csv_list = glob.glob(os.path.join(pwd, 'data/pd/5*.csv'))
    ppv_csv_list = glob.glob(os.path.join(pwd, 'data/ppv/5*.csv'))
    # c = ChargerDataClient(client_host, client_port, 1, 1)
    # c.send_pd_add_ev_data(543761864, pdcsv, ppvcsv, evcsv)
    c = ChargerDataServerAndClient('127.0.0.1', 50007, '0.0.0.0', 50008)
    c.send_recv_data(pd_csv_list, ppv_csv_list)
