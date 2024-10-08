import json
import math
import os
import socket
from settings import *

FILE_TYPE = {
    "image": ['.jpg', '.jpeg', '.png', '.gif'],
    "video": ['.mp4', '.avi', '.mov', '.mp3', '.wav', '.mkv'],
    "pdf": ['.pdf'],
    "markdown": ['.md'],
    "html": ['.html', '.htm']
}

def condition_assert(message, condition=False) -> None:
    """
    exit if condition is not satisfied
    """
    if not condition:
        print(message)
        print('Exit.')
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

# --- file operations ---

def convert_size(size_bytes: int) -> str:
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
    if not os.path.isdir(path): # path not exist
        return []

    files = os.listdir(path)
    file_list = []
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            file_info = {
                "name": file,
                "size": convert_size(os.path.getsize(file_path)),
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

def make_unique(path:str, file_name:str) -> tuple:
    """
    make file name unique

    :param path: file path (folder path)
    :param file_name: file name
    :return: (unique file path, uinque file name)
    """
    exist_names = os.listdir(path)
    first_name, last_name = os.path.splitext(file_name)
    name = [first_name, last_name, 0] # file name, file extension, file number(0 means no number)
    make_name = lambda x:x[0]+(f"({str(x[2])})"if x[2]!=0 else "")+x[1] # concat file name
    while True:
        if not make_name(name) in exist_names: # file name is unique
            break
        name[2] += 1 # existing name, add number
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
        result = json.loads(data)
    return result

def write_file(file_path:str, data) -> None:
    """
    write json file
    
    :param file_path: file path
    """
    with open(file_path,"w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=True)

def get_filetype(file_path:str) -> str:
    """
    get file type
    
    :param file_path: file path 
    :return: file type
    """
    extension = os.path.splitext(file_path)[1].lower() # get file extension
    file_type = "other"
    for type_ in FILE_TYPE.keys():
        if extension in FILE_TYPE[type_]:
            file_type = type_
            break
    return file_type

