import configparser
import os
from global_vars.funcs import create_folders
from global_vars.vars import ini_global_path

def check_structure(config):
    if "DATABASE" in config.sections():
        if os.path.exists(config["Database"]["path"]):
            return True
    return False

def create_config_parser(db_path=None):
    config = configparser.ConfigParser()

    if os.path.exists(ini_global_path):
        config.read(ini_global_path)
        if check_structure(config):
            return

    if db_path is None:
        db_path = f"{os.environ["LocalAppData"]}/KittingOptimization/database/shop_orders.db"


    config["DATABASE"] = {"Path": db_path,}


    create_folders(ini_global_path)
    # Write the config to a file
    with open(ini_global_path, 'w') as configfile:
        config.write(configfile)
    return



