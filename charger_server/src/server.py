import os
import glob
from datetime import datetime
from typing import List, Dict

import yaml
from flask import Flask, jsonify, request, render_template, url_for
from flask_cors import CORS

import schemas
try:
    from .pvmesh_graph.graph_writer import Neo4jDataClient
except ImportError:
    from pvmesh_graph.graph_writer import Neo4jDataClient
try:
    from .create_data import CreateDataFields
except ImportError:
    from create_data import CreateDataFields


app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

yaml_conf_path = os.path.join(os.path.dirname(__file__), 'config/config.yaml')
with open(yaml_conf_path, 'r') as yml:
    config = yaml.safe_load(yml)
    graphdb = Neo4jDataClient(**config['Neo4j'])

# pd_csv_path_list = glob.glob(os.path.join(
#     os.path.dirname(__file__), 'data/pd/*.csv'))
# ppv_csv_path_list = glob.glob(os.path.join(
#     os.path.dirname(__file__), 'data/ppv/*.csv'))

# ファイルデータ
pd_ppv = CreateDataFields()


@app.route('/', methods=['POST'])
def charger_update():
    request_json: schemas.PostEV = request.get_json()
    for ev in request_json['EV_stat']:
        meshcode, charge_val, car_id = ev['meshcode'], ev['charge'], ev['CarID']
        # 現在地がChargerのmeshcodeであるとき
        if meshcode in pd_ppv.data_fields.keys():
            # pd_ppv.tmp_charge_vals_add(meshcode=meshcode, value=charge_val)
            # EVの充電量をpdに足す
            pd_ppv.data_fields[meshcode]['pd'][pd_ppv.idx][1] += charge_val
            # 各メッシュで充電中のCarID
            pd_ppv.EV_charging_append(meshcode=meshcode, car_id=car_id)
            # 充電量が0ならCarIDを削除
            if not charge_val:
                pd_ppv.EV_charging[meshcode].remove(car_id)
    # print(pd_ppv.EV_charging)
    record_minutes = datetime.strptime(
        request_json['time'], '%Y-%m-%d %H:%M:%S').minute
    if (record_minutes == 0) or (record_minutes == 30):
        params = pd_ppv.get_current_idx_data()
        for param in params.values():
            # graphdb.update_charger_graph(param)
            print(param['time'], param['pd'])
        pd_ppv.idx_count_up()
        return jsonify({'data': pd_ppv.data_fields[543771291]['pd'][pd_ppv.idx]})
    else:
        return jsonify(request_json)


# @app.route('/', methods=['POST'])
# def charger_update():
#     request_json: schemas.PostEV = request.get_json()
#     meshcode, charge = request_json['meshcode'], request_json['charge']
#     print(request_json)
#     is_meshcode = pd_ppv_data.data_fields.get(meshcode)
#     if is_meshcode:
#         pd_ppv_data.tmp_charge_values_update(meshcode, charge)
#     record_minutes = datetime.strptime(
#         request_json['time'], '%Y-%m-%d %H:%M:%S').minute
#     if (record_minutes == 0) or (record_minutes == 30):
#         pd_ppv_data.data_fields_add_charge_value()
#         params = pd_ppv_data.get_current_idx_data_fields()
#         for param in params.values():
#             graphdb.update_charger_graph(param)
#         pd_ppv_data.idx_count_up()
#         return jsonify(params)
#     else:
#         return jsonify(request_json)


@app.route('/latest/', methods=['GET'])
def get_charger_props_latest():
    return graphdb.get_charger_props_latest()


@app.route('/plot/', methods=['GET'])
def line_plot() -> List[schemas.ChartjsFmt]:
    records_hash: Dict[int, List[dict]] = {}
    for props in graphdb.get_charger_props():
        meshcode = props['meshcode']
        if meshcode not in records_hash.keys():
            records_hash[meshcode] = [props]
        else:
            records_hash[meshcode].append(props)
    chartjs_data = []
    for meshcode in records_hash.keys():
        data = {
            'meshcode': meshcode,
            'time': [record['time'] for record in records_hash[meshcode]],
            'ppv': [record['ppv'] for record in records_hash[meshcode]],
            'pd': [record['pd'] for record in records_hash[meshcode]],
            'ppv-pd': [record['ppv']-record['pd'] for record in records_hash[meshcode]]
        }
        chartjs_data.append(data)
    # return chartjs_fmt
    # return render_template('index.html', chartjs_data=chartjs_data)
    return jsonify({'data': chartjs_data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50001, threaded=True, debug=True)
