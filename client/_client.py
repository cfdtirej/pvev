import csv
import json
import socket
import time
import os

import yaml

from multiprocessing import Process


def field_type_conv(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        field_array = []
        for row in reader:
            line = []
            for v in row:
                try:
                    value = float(v)
                except ValueError:
                    value = str(v)
                line.append(value)
            field_array.append(line)
    del field_array[0]
    return field_array


def charger_init_data(pd_csv='./data/pd/charger_pd.csv', ppv_csv='./data/ppv/charger_ppv.csv'):
    init_data = {
        '543771363': [], '543771054': [], '543761864': [], '543771291': []
    }
    for pd, ppv in zip(field_type_conv(pd_csv), field_type_conv(ppv_csv)):
        init_data['543771363'].append([pd[0], pd[1], ppv[1]])
        init_data['543771054'].append([pd[0], pd[2], ppv[2]])
        init_data['543761864'].append([pd[0], pd[3], ppv[3]])
        init_data['543771291'].append([pd[0], pd[4], ppv[4]])
    return init_data


class ChargerDataClient:
    def __init__(self,  client_host, client_port, server_port=None,):
        self.client_host = client_host
        self.client_port = client_port
        self.server_port = server_port

    def send_init_data(self, meshcode):
        """
        :param meshcode:  Select from the meshcode below
            - '543771363'
            - '543771054'
            - '543761864'
            - '543771291'
        :param charger_data:
        :return:
        """
        charger_data = charger_init_data()[meshcode]
        counter = [_ for _ in range(1, 7)]
        exception_counter = counter.copy()
        while True:
            if time.time() % 10 == 0:
                break
        print("======RUN=====>")
        cnt = 0
        while True:
            if time.time() % 3 == 0:
                times = [charger_data[cnt][0]]
                pd_data = [charger_data[cnt][1]]
                ppv_data = [charger_data[cnt][2]]
                for idx in range(len(counter)):
                    if cnt < len(charger_data) - len(counter):
                        pd_data.append(charger_data[counter[idx] + cnt][1])
                        ppv_data.append(charger_data[counter[idx] + cnt][2])
                    elif cnt >= len(charger_data) - len(counter):
                        try:
                            pd_data.append(charger_data[counter[idx] + cnt][1])
                            ppv_data.append(
                                charger_data[counter[idx] + cnt][2])
                        except IndexError:
                            if exception_counter[idx] == counter[idx]:
                                exception_counter[idx] = 0
                            pd_data.append(
                                charger_data[exception_counter[idx]][1])
                            ppv_data.append(
                                charger_data[exception_counter[idx]][2])
                            if exception_counter[idx] != counter[idx]:
                                exception_counter[idx] += 1

                send_json = {
                    'meshcode': int(meshcode), 'time': '2020-08-02T'+times[0]+'+09:00',
                    'ppv': ppv_data[0], 'ppv_030': ppv_data[1], 'ppv_060': ppv_data[2],
                    'ppv_090': ppv_data[3], 'ppv_120': ppv_data[4], 'ppv_150': ppv_data[5], 'ppv_180': ppv_data[6],
                    'pd': pd_data[0], 'pd_030': pd_data[1], 'pd_060': pd_data[2],
                    'pd_090': pd_data[3], 'pd_120': pd_data[4], 'pd_150': pd_data[5], 'pd_180': pd_data[6]
                }
                print(f'{meshcode} {cnt} {send_json} \n')

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.connect((self.client_host, self.client_port))
                    client.sendall(json.dumps(send_json).encode('utf-8'))
                    print(repr(client.recv(1024)))
                cnt += 1
            if cnt == 48:
                break

    def run_serv_(self, meshcode):
        """
        :param meshcode:  Select from the meshcode below
            - '543771363'
            - '543771054'
            - '543761864'
            - '543771291'
        :param charger_data:
        :return:
        """
        charger_data = charger_init_data()[meshcode]
        counter = [_ for _ in range(1, 7)]
        exception_counter = counter.copy()
        while True:
            if time.time() % 10 == 0:
                break
        print("======RUN=====>")
        cnt = 0
        while True:
            if time.time() % 3 == 0:
                times = [charger_data[cnt][0]]
                pd_data = [charger_data[cnt][1]]
                ppv_data = [charger_data[cnt][2]]
                for idx in range(len(counter)):
                    if cnt < len(charger_data) - len(counter):
                        pd_data.append(charger_data[counter[idx] + cnt][1])
                        ppv_data.append(charger_data[counter[idx] + cnt][2])
                    elif cnt >= len(charger_data) - len(counter):
                        try:
                            pd_data.append(charger_data[counter[idx] + cnt][1])
                            ppv_data.append(
                                charger_data[counter[idx] + cnt][2])
                        except IndexError:
                            if exception_counter[idx] == counter[idx]:
                                exception_counter[idx] = 0
                            pd_data.append(
                                charger_data[exception_counter[idx]][1])
                            ppv_data.append(
                                charger_data[exception_counter[idx]][2])
                            if exception_counter[idx] != counter[idx]:
                                exception_counter[idx] += 1

                send_json = {
                    'meshcode': int(meshcode), 'time': '2020-08-02T'+times[0]+'+09:00',
                    'ppv': ppv_data[0], 'ppv_030': ppv_data[1], 'ppv_060': ppv_data[2],
                    'ppv_090': ppv_data[3], 'ppv_120': ppv_data[4], 'ppv_150': ppv_data[5], 'ppv_180': ppv_data[6],
                    'pd': pd_data[0], 'pd_030': pd_data[1], 'pd_060': pd_data[2],
                    'pd_090': pd_data[3], 'pd_120': pd_data[4], 'pd_150': pd_data[5], 'pd_180': pd_data[6]
                }
                print(f'{meshcode} {cnt} {send_json} \n')

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.connect((self.client_host, self.client_port))
                    client.sendall(json.dumps(send_json).encode('utf-8'))
                    print(repr(client.recv(1024)))
                cnt += 1
            if cnt == 48:
                break


def init_data_client(host, port):
    client = ChargerDataClient(host, port)
    charger_client = client.send_init_data
    north_charger = Process(target=charger_client, args=('543771363',))
    west_charger = Process(target=charger_client, args=('543771054',))
    south_charger = Process(target=charger_client, args=('543761864',))
    east_charger = Process(target=charger_client, args=('543771291',))
    north_charger.start()
    west_charger.start()
    south_charger.start()
    east_charger.start()


if __name__ == '__main__':
    yaml_config = os.path.join(os.path.dirname(__file__), 'config/config.yaml')
    with open(yaml_config, 'r') as yf:
        config = yaml.safe_load(yf)
        Host = config["SocketClient"]["host"]
        Port = config["SocketClient"]["port"]
        north_mesh = '543771363'
        west_mesh = '543771054'
        south_mesh = '543761864'
        east_mesh = '543771291'

    init_data_client(Host, Port)
