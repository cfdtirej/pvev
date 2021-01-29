from pathlib import Path

import yaml

# config
with open(Path(__file__).parent / 'config' / 'config.yaml', 'r') as f:
    conf = yaml.safe_load(f)

# data files list
data_dir = Path(__file__).parent / 'data'
pd_files = list(data_dir.glob('pd/*.csv'))
ppv_files = list(data_dir.glob('ppv/*.csv'))
