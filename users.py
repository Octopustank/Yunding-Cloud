import os
import utils
import tokens
import hashlib
from settings import *

def _read_user_roots(user_list:list) -> dict:
    """
    get user folders

    :param user_list: user list
    :return: user folders:
        {
            user1: {
                "private": user1 private folder path,
                "sahre": user1 sahre folder path
            },
            ...
        }
    """
    make_private_path = lambda user, sub_folder: os.path.join(HOME_ROOT, user, sub_folder)
    user_folders = {user: {"private": make_private_path(user, PRIVATE_FOLDER),
                           "share": make_private_path(SHARE_USER, user)}
                           for user in user_list}
    return user_folders

def encrypt_pwd(pwd:str) -> str:
    """
    encrypt password
    
    :param pwd: password
    :return: encrypted password
    """

    encrypted_pwd = hashlib.sha1(pwd.encode('utf-8')).hexdigest()
    return encrypted_pwd

def get_user_loginInfo() -> dict:
    """
    get user login info

    :return: user login info
    """
    
    return utils.read_file(LOGIN_PATH)

def get_user_folders() -> dict:
    """
    get user folders

    :return: user folders:
        {
            user1: {
                "private": user1 private folder path,
                "share": user1 share folder path
            },
            ...
        }
    """
    
    user_folders = _read_user_roots(USER_LIST)
    return user_folders

def check_user(uid:str) -> bool:
    """
    check user exist
    
    :param uid: user id
    :return: 0: user not exist, 1: user exist, -1: user pwd reseted
    """
    if uid in USER_LIST:
        if get_user_loginInfo().get(uid) == -1:
            return -1
        return 1
    else:
        return 0

def login(uid:str, pwd:str) -> bool:
    """
    login
    
    :param uid: user id
    :param pwd: password
    :return: 0: login failed, 1: login success, -1: user not exist
    """

    login_info = get_user_loginInfo()
    encrypted_pwd = login_info.get(uid)

    if encrypted_pwd == encrypt_pwd(pwd): # login success
        return 1
    elif encrypted_pwd is None: # user not exist
        return -1
    else: # password error
        return 0

def change_pwd(uid:str, new_pwd:str) -> None:
    """
    change password
    
    :param uid: user id
    :param pwd: password
    """
    
    login_info = get_user_loginInfo()
    login_info[uid] = encrypt_pwd(new_pwd)
    utils.write_file(LOGIN_PATH, login_info)

def get_absPath(uid:str, private_path:str) -> str:
    """
    trans private path to absolute path

    :param uid: user id
    :param private_path: private path
    :return: absolute path
    """
    if private_path is None or private_path == "":
        return None
    if uid not in USER_LIST:
        return None
    
    path_split = private_path.split("/")

    folder_base = None # get base folder
    if path_split[0] == "public":
        folder_base = PUBLIC_PATH
    elif path_split[0] == "visit":
        if len(path_split) == 1: # user list folder
            return "visit"
        if path_split[1] not in USER_LIST:
            return None
        folder_base = get_user_folders()[path_split[1]]["share"]
        path_split.pop(0)
    else:
        folder_base = get_user_folders()[uid].get(path_split[0])
    if folder_base is None: # base folder not exist
        return None
    
    tar_path = os.path.join(folder_base, "/".join(path_split[1:]))
    return tar_path


def check_login(session: dict):
    """
    check login status
    
    :return: False: not login, str: login user id
    """
    token = session.get(SESSION_KEYNAME)
    if token is None:
        return False
    
    token_value = tokens.get_token_value(token)
    if token_value is None or token_value[0] != "account" or token_value[1] not in USER_LIST: # invalid account token
        return False
    
    return token_value[1]

def login_register(uid:str) -> str:
    """
    login

    :param uid: user id
    :return: login token(None: login fail)
    """
    if uid not in USER_LIST:
        return None
    token = tokens.make_token(uid, "account")
    return token

def logout(token:str) -> bool:
    """
    logout

    :param token: login token
    :return: True: logout success, False: logout fail
    """
    if token is None:
        return False
    return tokens.destroy_token(token)