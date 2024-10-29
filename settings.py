import os
import json
from utils import condition_assert, info, read_file, write_file, getip

PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(PATH, "data")
SETTINGS_PATH = os.path.join(PATH, "settings.json")
LOGIN_PATH = os.path.join(DATA_PATH, "login.json")
TOKEN_PATH = os.path.join(DATA_PATH, "tokens.json")

_vars = {
    "server.ip": "0.0.0.0", # where the server runs
    "server.port": 1145, # server port
    "server.debug": True, # debug mode
    "server.protocol": "http", # server protocol (http or https)
    "server.addr": None, # server address for users to visit (used for file share) (e.g. 192.168.1.10:1145 or example.com)
    "server.session_keyname": "Yunding_key", # key name of login token in session

    "cloud.file_max_size": 5 * 1024 * 1024 * 1024, # max file size
        
    "folder.home_root": "./home", # root folder of all users
    "folder.private": "private", # name of pricate folder in each user's home
    "folder.public": "public", # name of public folder in shared user's home

    "user.shared": "share", # shared user name
    "user.list": [], # list of all users

    "token.valid_time": 24 * 60 * 60 # token valid time (seconds) (for login and file share)
}

"""
load settings from file
"""
condition_assert(os.path.exists(SETTINGS_PATH), "settings file not exists")
with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
    _vars.update(json.load(f))

"""
extract settings
"""
# -- server vars --
IP = _vars["server.ip"]
PORT = _vars["server.port"]
DEBUG = _vars["server.debug"]
PROTOCOL = _vars["server.protocol"]
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


"""
process settings
"""
# concat paths
PUBLIC_PATH = os.path.join(HOME_ROOT, SHARE_USER, PUBLIC_FOLDER)

# check ip
if IP is None:
    IP = getip()
    info(f"server ip not set. Automatically set to {IP}")
if SERVER_ADDR is None:
    SERVER_ADDR = f"{getip()}:{PORT}"
    info(f"server address not set. Automatically set to {SERVER_ADDR}")

# check data
if not os.path.exists(DATA_PATH):
    info("data folder not exists. Automatically created.")
    os.mkdir(DATA_PATH)

if not os.path.exists(LOGIN_PATH):
    info("login.json not exists. Automatically created.")
    _login_dict = {_user: -1 for _user in USER_LIST}
    write_file(LOGIN_PATH, _login_dict)
else:
    _login_dict = read_file(LOGIN_PATH)
    condition_assert(type(_login_dict) == dict, "login.json is not a dict")
    for _user in USER_LIST:
        if not _user in _login_dict:
            _login_dict[_user] = -1 # add user and set password to -1 (not set)
    for _user in _login_dict:
        if not _user in USER_LIST: # user not exists
            del _login_dict[_user] # delete user
    write_file(LOGIN_PATH, _login_dict)

if not os.path.exists(TOKEN_PATH):
    info("tokens.json not exists. Automatically created.")
    write_file(TOKEN_PATH, {})
else:
    _tokens = read_file(TOKEN_PATH)
    condition_assert(type(_tokens) == dict, "tokens.json is not a dict")

# check folder exists
condition_assert(os.path.exists(HOME_ROOT), f"home root folder not exists. It should be {HOME_ROOT}")
condition_assert(os.path.exists(PUBLIC_PATH), f"public folder not exists. It should be {PUBLIC_PATH}")
for _user in USER_LIST:
    _private_folder = os.path.join(HOME_ROOT, _user, PRIVATE_FOLDER)
    _shared_folder = os.path.join(HOME_ROOT, SHARE_USER, _user)
    condition_assert(os.path.exists(_private_folder),
                    f"{_user}'s private folder not exists. It should be {_private_folder}")
    condition_assert(os.path.exists(_shared_folder),
                    f"{_user}'s shared folder not exists. It should be {_shared_folder}")

