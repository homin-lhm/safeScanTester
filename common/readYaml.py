import yaml


def read_yaml(file):
    with open(file=file, mode='r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


