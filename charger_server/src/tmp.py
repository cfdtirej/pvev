from flask import Flask, jsonify
from typing import List, Dict

import settings
import schemas
try:
    from .pvmesh_graph.graph_writer import Neo4jDataClient
except ImportError:
    from pvmesh_graph.graph_writer import Neo4jDataClient


client = Neo4jDataClient(**settings.conf['Neo4j'])
charger_props_all = client.get_charger_props()


def charger_props_chartjs_fmt() -> List[schemas.ChartjsFmt]:
    records_hash: Dict[int, List[dict]] = {}
    for props in charger_props_all:
        meshcode = props['meshcode']
        if meshcode not in records_hash.keys():
            records_hash[meshcode] = [props]
        else:
            records_hash[meshcode].append(props)
    chartjs_fmt = []
    for meshcode in records_hash.keys():
        data = {
            'meshcode': meshcode,
            'time': [record['time'] for record in records_hash[meshcode]],
            'ppv': [record['ppv'] for record in records_hash[meshcode]],
            'pd': [record['pd'] for record in records_hash[meshcode]],
            'pd-ppv': [record['pd']-record['ppv'] for record in records_hash[meshcode]]
        }
        chartjs_fmt.append(data)
    return chartjs_fmt


data = (charger_props_chartjs_fmt())
d = data[0]['pd-ppv']+data[1]['pd-ppv']+data[2]['pd-ppv']+data[3]['pd-ppv']
print(d)
