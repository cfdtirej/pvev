from pathlib import Path

import yaml

try:
    from .pvmesh_graph.graph_writer import Neo4jDataClient
except ImportError:
    from pvmesh_graph.graph_writer import Neo4jDataClient


conf_yaml = Path(__file__).parent / 'config/config.yaml'


# Chargerのデータを全削除
def delete_charger():
    with open(conf_yaml, 'r') as f:
        config = yaml.safe_load(f)
        graphdb = Neo4jDataClient(**config['Neo4j'])
        graphdb.delete_charger()


if __name__ == '__main__':
    delete_charger()
