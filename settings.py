import os
import json

PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(PATH, "data")
SETTINGS_PATH = os.path.join(PATH, "settings.json")
LOGIN_PATH = os.path.join(DATA_PATH, "login.json")
TOKEN_PATH = os.path.join(DATA_PATH, "tokens.json")

_vars = {
    "server.ip": "0.0.0.0",
    "server.port": 1145,
    "server.debug": True,
    "server.addr": "http://101.7.170.231:1145",
    "server.session_keyname": "Yunding_key",

    "cloud.file_max_size": 5 * 1024 * 1024 * 1024,
        
    "folder.home_root": "./home",
    "folder.private": "private",
    "folder.public": "public",

    "user.shared": "share",
    "user.list": [],

    "token.valid_time": 24 * 60 * 60
}

with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
    _vars.update(json.load(f))


# -- server vars --
IP = _vars["server.ip"]
PORT = _vars["server.port"]
DEBUG = _vars["server.debug"]
SERVER_ADDR = _vars["server.addr"]
SESSION_KEYNAME = _vars["server.session_keyname"]

# -- cloud vars --
FILE_MAXSIZE = _vars["cloud.file_max_size"]

# -- folder vars --
HOME_ROOT = _vars["folder.home_root"]
PRIVATE_FOLDER = _vars["folder.private"]
PUBLIC_FOLDER = _vars["folder.public"]

# -- user vars --
SHARE_USER = _vars["user.shared"]
USER_LIST = _vars["user.list"]

# -- token vars --
TOKEN_VALID_TIME = _vars["token.valid_time"]


# concat paths
PUBLIC_PATH = os.path.join(HOME_ROOT, SHARE_USER, PUBLIC_FOLDER)

