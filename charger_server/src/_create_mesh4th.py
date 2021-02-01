from pathlib import Path

import yaml

try:
    from .pvmesh_graph.graph_writer import Neo4jDataClient
except ImportError:
    from pvmesh_graph.graph_writer import Neo4jDataClient


conf_yaml = Path(__file__).parent / 'config/config.yaml'

# ４次メッシュグラフの作成
def create_mesh4th():
    with open(conf_yaml, 'r') as f:
        config = yaml.safe_load(f)
        graphdb = Neo4jDataClient(**config['Neo4j'])
        graphdb.create_init_mesh4th_graph()


if __name__ == '__main__':
    create_mesh4th()