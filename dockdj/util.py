from typing import Dict
import os
from dockdj.du_settings import CONFIG_FILE, SETTINGS_PY_FILE
import yaml
from sys import exit


def read_config_files() -> (Dict, str):
    if not os.path.isfile(CONFIG_FILE):
        print(f'Please run "dockdj" init to create {CONFIG_FILE} file')
        exit()

    if not os.path.isfile(SETTINGS_PY_FILE):
        print(f'Please run "dockdj init" to create {SETTINGS_PY_FILE} file')
        exit()

    with open(CONFIG_FILE, 'r') as the_file:
        config_yaml = yaml.load(the_file)

    with open(SETTINGS_PY_FILE, 'r') as the_file:
        settings_py = the_file.read()

    return config_yaml, settings_py
