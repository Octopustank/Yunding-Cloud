import os
import utils

LOGIN_PATH = os.path.join(utils.DATA_PATH, "login.json")
SESSION_KEYNAME = "Yunding_key"

def check_workdir() -> None:
    utils.condition_assert(f"Login path({LOGIN_PATH}) is not exist", os.path.isfile(LOGIN_PATH))
    try:
        users = get_users()
    except:
        utils.condition_assert("Login file is not valid", False)
    for user in users:
        user_private_path = os.path.join(utils.HOME_ROOT, user, utils.PRIVATE_FOLDER)
        user_share_path = os.path.join(utils.HOME_ROOT, utils.SHARE_USER, user)
        utils.condition_assert(f"User {user} private folder is not exist", os.path.isdir(user_private_path))
        utils.condition_assert(f"User {user} share folder is not exist", os.path.isdir(user_share_path))

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
    make_private_path = lambda user, sub_folder: os.path.join(utils.HOME_ROOT, user, sub_folder)
    user_folders = {user: {"private": make_private_path(user, utils.PRIVATE_FOLDER),
                           "share": make_private_path(utils.SHARE_USER, user)}
                           for user in user_list}
    return user_folders

def get_user_loginInfo() -> dict:
    """
    get user login info

    :return: user login info
    """
    
    return utils.read_file(LOGIN_PATH)

def get_users() -> list:
    """
    get user list

    :return: user list
    """
    
    return get_user_loginInfo().keys()

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

def login(uid:str, pwd:str) -> bool:
    """
    login
    
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

    folder_base = None # get base folder
    if path_split[0] == "public":
        folder_base = utils.PUBLIC_PATH
    elif path_split[0] == "visit":
        if len(path_split) == 1: # user list folder
            return "visit"
        if path_split[1] not in get_users():
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
    key = session.get(SESSION_KEYNAME)
    if key is None:
        return False
    
    key_value = utils.get_key_value(key)
    if key_value is None or key_value[0] != "account" or key_value[1] not in get_users(): # invalid account key
        return False
    
    return key_value[1]

def login_register(uid:str) -> str:
    """
    login

    :param uid: user id
    :return: login key(None: login fail)
    """
    if uid not in get_users():
        return None
    key = utils.make_key(uid, "account")
    return key

def logout(key:str) -> bool:
    """
    logout

    :param key: login key
    :return: True: logout success, False: logout fail
    """
    if key is None:
        return False
    return utils.destroy_key(key)