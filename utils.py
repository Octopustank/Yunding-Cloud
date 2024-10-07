"""
utils for server
"""

import json as js
import math
import os
import socket
import hashlib
from flask import make_response, send_file, Response
import markdown
from urllib.parse import quote

PRIVATE_FOLDER = "private" # private folder name in user folder (owner rw, others --)
SHARE_FOLDER = "share" # share folder name in `share` folder (owner rw, others r-)
PUBLIC_FOLDER = "public" # public folder name in `share` folder (all rw)

SHARE_USER = "share" # share user name

FILE_TYPE = {
    "image": ['.jpg', '.jpeg', '.png', '.gif'],
    "video": ['.mp4', '.avi', '.mov', '.mp3', '.wav', '.mkv'],
    "pdf": ['.pdf'],
    "markdown": ['.md']
}

PATH = os.path.dirname(os.path.abspath(__file__))
HOME_ROOT = os.path.join(PATH, "home")
DATA_PATH = os.path.join(PATH, "data")
PUBLIC_PATH = os.path.join(HOME_ROOT, SHARE_USER, PUBLIC_FOLDER)

USER_LIST = []

def condition_assert(message, condition=False) -> None:
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
    print(path)
    if not os.path.isdir(path): # path not exist
        return []

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
    print(file_list)
    return file_list

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

def get_filetype(file_path:str) -> str:
    """
    get file type
    
    :param file_path: file path 
    :return: file type
    """
    extension = os.path.splitext(file_path)[1].lower() # get file extension
    file_type = "other"
    for key in FILE_TYPE.keys():
        if extension in FILE_TYPE[key]:
            file_type = key
            break
    return file_type

def make_preview_response(file_path:str, file_type:str) -> Response:
    """
    make file preview response
    
    :param file_path: file path
    :param file_type: file type
    :return: response
    """
    # make response according to file type
    if file_type == "image":
        with open(file_path, 'rb') as f:  
            response = make_response(f.read())  
            response.headers['Content-Type'] = 'image/jpeg' # set Content-Type
            return response  
    elif file_type == "video":
        with open(file_path, 'rb') as f:
            response = make_response(f.read())
            response.headers['Content-Type'] = 'video/mp4'
            return response
    elif file_type == "pdf":
        with open(file_path, 'rb') as f:
            response = make_response(f.read())
            response.headers['Content-Type'] = 'application/pdf'
            return response
    elif file_type == "markdown":
        with open(file_path, 'r', encoding="utf-8") as f:
            md_content = f.read()
            html_content = markdown.markdown(md_content)
            response = make_response(html_content)
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response
    else:
        try: # try to open as text
            with open(file_path, 'r', encoding="utf-8") as f:
                response = make_response(f.read())
                response.headers['Content-Type'] = 'text/plain; charset=utf-8'
                return response
        except:
            return "Unsupported file type", 400

def make_download_response(file_path:str) -> Response:
    """
    make file download response

    :param file_path: file path
    :return: response
    """
    if os.path.isfile(file_path): # is file
        # make download response
        file_name = quote(os.path.split(file_path)[-1]) # transfer file name to UTF-8
        file_response = send_file(file_path, as_attachment=True, download_name=file_name)
        file_response.headers["Content-Disposition"] += ";filename*=utf-8''{}".format(file_name) # set Content-Disposition, transfer file name to UTF-8
        return file_response
    else:
        return "File not exist", 404

def encrypt_pwd(pwd:str) -> str:
    """
    encrypt password
    
    :param pwd: password
    :return: encrypted password
    """

    encrypted_pwd = hashlib.sha1(pwd.encode('utf-8')).hexdigest()
    return encrypted_pwd
