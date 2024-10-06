"""
utils for server
"""

import json as js
import math
import os
import socket
import hashlib

PRIVATE_FOLDER = "private" # private folder name in user folder
PUBLIC_FOLDER = "public" # public folder name in `share` folder
SHARE_USER = "share" # share user name

PATH = os.path.dirname(os.path.abspath(__file__))
HOME_ROOT = os.path.join(PATH, "home")
DATA_PATH = os.path.join(PATH, "data")
USER_LIST = []

def _read_user_roots(user_list:list) -> dict:
    """
    get user folders

    :param user_list: user list
    :return: user folders:
        {
            user1: {
                "private": user1 private folder path,
                "public": user1 public folder path
            },
            ...
        }
    """
    make_private_path = lambda user, sub_folder: os.path.join(HOME_ROOT, user, sub_folder)
    user_folders = {user: {"private": make_private_path(user, PRIVATE_FOLDER),
                           "public": make_private_path(SHARE_USER, user)}
                           for user in user_list}
    return user_folders

def _convert_size(size_bytes: int) -> str:
    """
    convert bytes to human readable size

    :param size_bytes: size in bytes
    :return: human readable size
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def list_dir(path: str) -> list:
    """
    list files and info in the folder

    :param path: folder path
    :return: file list [dict{"name":str, "size":str, "file":bool},...]
    """
    files = os.listdir(path)
    file_list = []
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            file_info = {
                "name": file,
                "size": _convert_size(os.path.getsize(file_path)),
                "file": True
            }
        else:
            file_info = {
                "name": file,
                "size": "",
                "file": False
            }
        file_list.append(file_info)
    return file_list

def condition_assert(message, condition=False):
    """
    exit if condition is not satisfied
    """
    if not condition:
        print(message)
        print('Press any key to exit...')
        exit(1)

def getip() -> str:
    """
    get server ip address
    :return: ip address
    """
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    except Exception as err:
        condition_assert(f"Network Error: {err}")
    finally:
        s.close()
    return ip

def make_unique(path:str, file_name:str) -> tuple:
    """
    make file name unique

    :param path: file path
    :param file_name: file name
    :return: (unique file path, uinque file name)
    """
    exist_names = os.listdir(path)
    first_name, last_name = os.path.splitext(file_name)
    name = [first_name, last_name, 0] # 文件名各部分和序号(若为0则实际不加)
    make_name = lambda x:x[0]+(f"({str(x[2])})"if x[2]!=0 else "")+x[1] # 拼接文件名函数
    while True:
        if not make_name(name) in exist_names: # 该文件名独一无二
            break
        name[2] += 1 # 该文件名已存在，序号增加
    name = make_name(name)
    return (os.path.join(path,name), name)

def read_file(file_path:str):
    """
    read json file
    
    :param file_path: file path
    :return: data(dict or list)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().encode(encoding='utf-8')
        result = js.loads(data)
    return result

def write_file(file_path:str, data) -> None:
    """
    write json file
    
    :param file_path: file path
    """
    with open(file_path,"w",encoding="utf-8") as f:
        js.dump(data, f, ensure_ascii=False, indent=True)

def get_user_info() -> dict:
    """
    get user dict

    :return: user info dict
    """
    
    user_file = os.path.join(DATA_PATH, "users.json")
    return read_file(user_file)

def get_users() -> list:
    """
    get user list

    :return: user list
    """
    
    user_info = get_user_info()
    return user_info.keys()

def get_user_loginInfo() -> dict:
    """
    get user login info

    :return: user login info
    """
    
    login_file = os.path.join(DATA_PATH, "login.json")
    return read_file(login_file)

def get_user_folders() -> dict:
    """
    get user folders
    """
    
    user_folders = _read_user_roots(get_users())
    return user_folders

def check_user(uid:str) -> bool:
    """
    check user exist
    
    :param uid: user id
    :return: 0: user not exist, 1: user exist, -1: user pwd reseted
    """
    if uid in get_users():
        if get_user_loginInfo().get(uid) == -1:
            return -1
        return 1
    else:
        return 0

def _encrypt_pwd(pwd:str) -> str:
    """
    encrypt password
    
    :param pwd: password
    :return: encrypted password
    """

    encrypted_pwd = hashlib.sha1(pwd.encode('utf-8')).hexdigest()
    return encrypted_pwd

def check_login(uid:str, pwd:str) -> bool:
    """
    check login
    
    :param uid: user id
    :param pwd: password
    :return: 0: login failed, 1: login success, -1: user not exist
    """

    login_info = get_user_loginInfo()
    encrypted_pwd = login_info.get(uid)

    if encrypted_pwd == _encrypt_pwd(pwd): # login success
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
    login_info[uid] = _encrypt_pwd(new_pwd)
    login_file = os.path.join(DATA_PATH, "login.json")
    write_file(login_file, login_info)