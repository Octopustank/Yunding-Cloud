import os
import utils

USER_PATH = os.path.join(utils.DATA_PATH, "users.json")
LOGIN_PATH = os.path.join(utils.DATA_PATH, "login.json")

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
    make_private_path = lambda user, sub_folder: os.path.join(utils.HOME_ROOT, user, sub_folder)
    user_folders = {user: {"private": make_private_path(user, utils.PRIVATE_FOLDER),
                           "share": make_private_path(utils.SHARE_USER, user)}
                           for user in user_list}
    return user_folders


def get_user_info() -> dict:
    """
    get user dict

    :return: user info dict
    """
    
    return utils.read_file(USER_PATH)

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
    
    return utils.read_file(LOGIN_PATH)

def get_user_folders() -> dict:
    """
    get user folders

    :return: user folders:
        {
            user1: {
                "private": user1 private folder path,
                "public": user1 public folder path
            },
            ...
        }
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

def check_login(uid:str, pwd:str) -> bool:
    """
    check login
    
    :param uid: user id
    :param pwd: password
    :return: 0: login failed, 1: login success, -1: user not exist
    """

    login_info = get_user_loginInfo()
    encrypted_pwd = login_info.get(uid)

    if encrypted_pwd == utils.encrypt_pwd(pwd): # login success
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
    login_info[uid] = utils.encrypt_pwd(new_pwd)
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
    if uid not in get_users():
        return None
    
    path_split = private_path.split("/")

    filter_base = None # get base folder
    if path_split[0] == "public":
        filter_base = utils.PUBLIC_PATH
    else:
        filter_base = get_user_folders()[uid].get(path_split[0])
    if filter_base is None: # base folder not exist
        return None
    
    tar_path = os.path.join(filter_base, "/".join(path_split[1:]))
    return tar_path

