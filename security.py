import hashlib
import time as tm
import os
import utils

# --- Configurations ---
KEY_VALID_TIME = 24 * 60 * 60 # key valid time (s)
# --- Configurations ---

KEY_PATH = os.path.join(utils.DATA_PATH, "keys.json")

def check_workdir() -> None:
    """
    check work directory
    """
    if not os.path.isfile(KEY_PATH):
        utils.write_file(KEY_PATH, {})
    try:
        read_keys()
    except:
        utils.condition_assert("Key file is invalid")

def encrypt_pwd(pwd:str) -> str:
    """
    encrypt password
    
    :param pwd: password
    :return: encrypted password
    """

    encrypted_pwd = hashlib.sha1(pwd.encode('utf-8')).hexdigest()
    return encrypted_pwd

def read_keys() -> dict:
    """
    read keys
    
    :return: keys ({key: {value: str, time: int}, ...})
    """
    keys = utils.read_file(KEY_PATH)
    return keys

def destroy_key(key:str) -> bool:
    """
    destroy key
    
    :param key: key
    :return: True: destroy success, False: destroy fail
    """
    keys = read_keys()
    if key not in keys.keys():
        return False
    keys.pop(key)
    utils.write_file(KEY_PATH, keys)
    return True

def check_keys() -> None:
    """
    check keys and destroy expired keys
    """
    keys = read_keys()
    cur_time = tm.time()
    for key in keys.keys():
        if keys[key]["time"] + KEY_VALID_TIME < cur_time: # key expired
            destroy_key(key)

def _gen_key(value:str) -> str:
    """
    generate key and save to file
    
    :param value: key value
    :return: key
    """
    keys = read_keys()
    cur_time = tm.time()
    key = hashlib.sha1((value + str(cur_time)).encode('utf-8')).hexdigest()
    keys[key] = {"value": value, "time": cur_time}
    utils.write_file(KEY_PATH, keys)
    return key

def make_key(value:str, type:str) -> str:
    """
    make key
    
    :param value: key value
    :param type: key type
    :return: key
    """
    return _gen_key(f"{type}-{value}")

def get_key_value(key:str) -> tuple:
    """
    get key value
    
    :param key: key
    :return: None if not valid, (value:str, type:str) if valid
    """
    check_keys() # destroy expired keys
    keys = read_keys()
    key_info = keys.get(key)
    if key_info is None: # key not exist
        return None
    key_value = key_info["value"].split("-")
    key_value = [key_value[0], "-".join(key_value[1:])]
    if len(key_value) != 2: # invalid format
        return None
    return tuple(key_value)
