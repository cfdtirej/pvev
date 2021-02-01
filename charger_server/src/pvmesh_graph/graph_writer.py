import json
import os
from datetime import datetime
from pprint import pprint

from neo4j import GraphDatabase, Record

try:
    from . import cypher_queries
except ImportError:
    import cypher_queries


north_south_length = 463
west_east_length = 559

mesh_json_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data/mesh4th.json')
with open(mesh_json_path, 'r') as jf:
    # Type is dict in list
    mesh4th = json.load(jf)["Mesh4th"]

mesh_json_v2_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data/mesh4th_v2.json')
with open(mesh_json_v2_path, 'r') as jf:
    # Key is string of meshcode
    mesh4th_key_mesh = json.load(jf)


class Neo4jDataClient:
    def __init__(self, url, user, password):
        self.driver = GraphDatabase.driver(
            url, auth=(user, password), encrypted=False)

    # 4次メッシュ道路の作成
    def create_init_mesh4th_graph(self):
        def merge_node_mesh4th(tx, params):
            tx.run(cypher_queries.merge_mesh4th, params)
        mesh4th_copy = mesh4th.copy()
        for mesh_param in mesh4th_copy:
            merge_param = {
                'name': 'Mesh_' + str(mesh_param['meshcode']),
                'longitude': mesh_param['longitude'],
                'latitude': mesh_param['latitude'],
                'meshcode': mesh_param['meshcode']
            }
            with self.driver.session() as session:
                session.write_transaction(merge_node_mesh4th, merge_param)

        def relate_mesh4th(tx, params):
            tx.run(cypher_queries.node_relating.replace(
                '#Lable', 'Mesh4th'), params)
        for related_param in mesh4th:
            main_param = dict(main_meshcode=related_param['meshcode'])
            for key, value in related_param['relation'].items():
                if value is None:
                    continue
                if key in ['north', 'south']:
                    param = main_param.copy()
                    param['to_meshcode'] = value
                    param['length'] = north_south_length
                    with self.driver.session() as session:
                        session.write_transaction(relate_mesh4th, param)
                elif key in ['west', 'east']:
                    param = main_param.copy()
                    param['to_meshcode'] = value
                    param['length'] = west_east_length
                    with self.driver.session() as session:
                        session.write_transaction(relate_mesh4th, param)

    # Chargerデータの追加
    def update_charger_graph(self, parameters):
        """
        :param parameters: dict
            keys:
                meshcode, ppv, ppv_030, ppv_060, ppv_090, ppv_120, ppv_150, ppv_180,
                pd, pd_030, pd_060, pd_090, pd_120, pd_150, pd_180, time
        :return:
        """
        def merger_charger_graph(tx, params):
            tx.run(cypher_queries.merge_charger_node, params)
        charger_param = mesh4th_key_mesh[str(parameters['meshcode'])].copy()
        charger_param.update(parameters)
        with self.driver.session() as session:
            del charger_param['relation']
            session.write_transaction(merger_charger_graph, charger_param)

    # 最新時刻のChargerデータをGET
    def get_charger_props_latest(self):
        with self.driver.session() as session:
            res = session.run(cypher_queries.get_charger_props)
            data_list = [dict(i) for i in res]
            data_list = sorted(data_list, key=lambda x: x['time'])
            key_list = list({d['meshcode'] for d in data_list})
            return {'charger_props': data_list[-len(key_list):]}

    # Chargerのpd,ppv, timeをmeshcodeごとに取得
    def get_pd_ppv(self):
        data_list = self.get_charger_props()['charger_props']
        charger_data = {k['meshcode']: [] for k in data_list}
        for data in data_list:
            charger_data[data['meshcode']].append(
                {'time': data['time'], 'pd': data['pd'], 'ppv': data['ppv'], 'meshcode': data['meshcode']})
        for k in charger_data.keys():
            sorted(charger_data[k], key=lambda x: x['time'])
        return charger_data

    def get_charger_props(self):
        with self.driver.session() as session:
            res = session.run(cypher_queries.get_charger_props)
            data_list = [dict(i) for i in res]
            data_list = sorted(data_list, key=lambda x: x['time'])
            key_list = list({d['meshcode'] for d in data_list})
            return data_list

    # chargerのmeshcodeの長さとリスト

    def get_charger_meshcode(self):
        with self.driver.session() as session:
            res = session.run(cypher_queries.charger_mesh)
            return [dict(i) for i in res][0]

    # Chargerグラフを全削除
    def delete_charger(self):
        def tx_run(tx):
            tx.run('MATCH (n:Charger) detach delete n')
        with self.driver.session() as session:
            session.write_transaction(tx_run)

    def get_sample(self):
        with self.driver.session() as session:
            res = session.run(cypher_queries.sample)
            data = [i['Data'] for i in res]
            return data


if __name__ == '__main__':
    from pathlib import Path
    import yaml
    with open(Path(__file__).parents[1]/'config'/'config.yaml', 'r') as f:
        conf = yaml.safe_load(f)
    client = Neo4jDataClient(**conf['Neo4j'])
    # data = client.get_sample()
