import csv
import glob
import os
import time

from datetime import datetime
from pprint import pprint
from pathlib import Path
from typing import List, Dict

import yaml
import schemas
try:
    from .pvmesh_graph.graph_writer import Neo4jDataClient
except ImportError:
    from pvmesh_graph.graph_writer import Neo4jDataClient


def to_rfc3339_jtc(timestamp: str) -> str:
    if '/' in timestamp:
        return datetime.strptime(timestamp.partition('.')[0]+'+0900', '%Y/%m/%d %H:%M:%S%z').isoformat()
    elif '-' in timestamp:
        return datetime.strptime(timestamp.partition('.')[0]+'+0900', '%Y-%m-%d %H:%M:%S%z').isoformat()


# Convert some files into a two-dimensional array dictionary keyed by meshcode
def some_csv_conv_data_fields(csvfiles: List[str]):
    result = {}
    for csvfile in csvfiles:
        with open(csvfile, 'r') as f:
            table = [_ for _ in csv.reader(f)]
            header = table.pop(0)
            field = [
                [to_rfc3339_jtc(i[0]), float(i[1])] for i in table
            ]
            result[int(header[1])] = field
    return result


data_dir = Path(__file__).parent / 'data'


class CreateDataFields:

    def __init__(self,
                 pd_csvfiles: List[str] = data_dir.glob('pd/*.csv'),
                 ppv_csvfiles: List[str] = data_dir.glob('ppv/*.csv')):
        """
        Parameters
        ----------
        pd_csv_list: PDのcsvファイルパスの文字列が入ったリスト
        ppv_csv_list: PPVのcsvファイルパスのH文字列が入ったリスト
        pdとppvのcsvのカラム名はmeshcodeの数値でファイル数も合わせてくれ〜
        """
        pd_fields = some_csv_conv_data_fields(pd_csvfiles)
        ppv_fields = some_csv_conv_data_fields(ppv_csvfiles)
        # 各meshcodeのpd,ppv
        self._data_fields: Dict[int, Dict[List[str, float]]] = {
            k: {'pd': pd_fields[k], 'ppv': ppv_fields[k]} for k in ppv_fields.keys()
        }
        # 充放電ポイント１つあたりのレコード数
        self._records_length: int = len((list(ppv_fields.values())[0]))
        # 充放電ポイントで充電中のEV
        self._EV_charging = {meshcode: [] for meshcode in ppv_fields.keys()}
        # 現在値と仮予測値のインデクス
        self._idx = 0
        self._idx_030 = -self._records_length + 1
        self._idx_060 = -self._records_length + 2
        self._idx_090 = -self._records_length + 3
        self._idx_120 = -self._records_length + 4
        self._idx_150 = -self._records_length + 5
        self._idx_180 = -self._records_length + 6

    @property
    def idx(self):
        return self._idx

    @property
    def data_fields(self):
        return self._data_fields

    @property
    def EV_charging(self):
        return self._EV_charging

    # Chargerで充電中のCarIDを追加
    def EV_charging_append(self, meshcode: int, car_id: int):
        self.EV_charging[meshcode].append(car_id)
        self.EV_charging[meshcode] = list(set(self.EV_charging[meshcode]))

    # index add 1
    def idx_count_up(self) -> None:
        self._idx += 1
        self._idx_030 += 1
        self._idx_060 += 1
        self._idx_090 += 1
        self._idx_120 += 1
        self._idx_150 += 1
        self._idx_180 += 1
        return

    # 現在(self._idx)のデータを取得
    def get_current_idx_data(self):
        parameters = {
            meshcode: {
                'meshcode': int(meshcode),
                'time': self._data_fields[meshcode]['pd'][self._idx][0],
                'pd': self._data_fields[meshcode]['pd'][self._idx][1],
                'pd_030': self._data_fields[meshcode]['pd'][self._idx_030][1],
                'pd_060': self._data_fields[meshcode]['pd'][self._idx_060][1],
                'pd_090': self._data_fields[meshcode]['pd'][self._idx_090][1],
                'pd_120': self._data_fields[meshcode]['pd'][self._idx_120][1],
                'pd_150': self._data_fields[meshcode]['pd'][self._idx_150][1],
                'pd_180': self._data_fields[meshcode]['pd'][self._idx_180][1],
                'ppv': self._data_fields[meshcode]['ppv'][self._idx][1],
                'ppv_030': self._data_fields[meshcode]['ppv'][self._idx_030][1],
                'ppv_060': self._data_fields[meshcode]['ppv'][self._idx_060][1],
                'ppv_090': self._data_fields[meshcode]['ppv'][self._idx_090][1],
                'ppv_120': self._data_fields[meshcode]['ppv'][self._idx_120][1],
                'ppv_150': self._data_fields[meshcode]['ppv'][self._idx_150][1],
                'ppv_180': self._data_fields[meshcode]['ppv'][self._idx_180][1],
            } for meshcode in self.data_fields.keys()
        }
        return parameters

    # EVの充電量を無視して1秒おきにChargerのデータを更新する
    def create_charger_file_data_only(self):
        yaml_conf_path = os.path.join(
            os.path.dirname(__file__), 'config/config.yaml')
        with open(yaml_conf_path, 'r') as yml:
            config = yaml.safe_load(yml)
        graphdb = Neo4jDataClient(**config['Neo4j'])
        for _ in range(self._records_length):
            params = self.get_current_idx_data()
            for param in params.values():
                graphdb.update_charger_graph(param)
            self.idx_count_up()
            time.sleep(1)


if __name__ == '__main__':
    pd = glob.glob('charger_server/src/data/pd/*.csv')
    ppv = glob.glob('charger_server/src/data/ppv/*.csv')
    power = CreateDataFields(pd, ppv)
    print(power.data_fields)
