import hashlib
import time as tm
import os
import utils
from settings import *

def read_tokens() -> dict:
    """
    read tokens
    
    :return: tokens ({token: {value: str, time: int}, ...})
    """
    tokens = utils.read_file(TOKEN_PATH)
    return tokens

def destroy_token(token:str) -> bool:
    """
    destroy token
    
    :param token: token
    :return: True: destroy success, False: destroy fail
    """
    tokens = read_tokens()
    if token not in tokens.keys():
        return False
    tokens.pop(token)
    utils.write_file(TOKEN_PATH, tokens)
    return True

def check_tokens() -> None:
    """
    check tokens and destroy expired tokens
    """
    tokens = read_tokens()
    cur_time = tm.time()
    for token in tokens.keys():
        if tokens[token]["time"] + TOKEN_VALID_TIME < cur_time: # token expired
            destroy_token(token)

def _gen_token(value:str) -> str:
    """
    generate token and save to file
    
    :param value: token value
    :return: token
    """
    tokens = read_tokens()
    cur_time = tm.time()
    token = hashlib.sha1((value + str(cur_time)).encode('utf-8')).hexdigest()
    tokens[token] = {"value": value, "time": cur_time}
    utils.write_file(TOKEN_PATH, tokens)
    return token

def make_token(value:str, type:str) -> str:
    """
    make token
    
    :param value: token value
    :param type: token type
    :return: token
    """
    return _gen_token(f"{type}-{value}")

def get_token_value(token:str) -> tuple:
    """
    get token value
    
    :param token: token
    :return: None if not valid, (value:str, type:str) if valid
    """
    check_tokens() # destroy expired tokens
    tokens = read_tokens()
    token_info = tokens.get(token)
    if token_info is None: # token not exist
        return None
    token_value = token_info["value"].split("-")
    token_value = [token_value[0], "-".join(token_value[1:])]
    if len(token_value) != 2: # invalid format
        return None
    return tuple(token_value)
