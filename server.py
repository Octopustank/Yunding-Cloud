from flask import Flask, render_template, request, redirect, flash, session
import os

import utils
import users
import security
import response

# --- Configurations ---
IP = "0.0.0.0"
PORT = 1145
DEBUG = True
SERVER_ADDR = "http://101.7.170.231:1145" # server address, for share link

FILE_MAXSIZE = 5 * 1024 * 1024 * 1024 # file max size
# --- Configurations ---

app = Flask("Cloud")
app.config['JSON_AS_ASCII'] = False
app.secret_key = "very-hard-to-guess-string"

@app.route("/")
def index():
    addr = request.remote_addr
    uid = users.check_login(session)
    banners = os.listdir("static/banners")
    banners = [f"/static/banners/{banner}" for banner in banners]
    return render_template("index.html", uid=uid if uid else None, addr=addr, banners=banners)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if users.check_login(session): # already login
        flash("Already login", "success")
        return redirect("/")
    if request.method == "POST": # filled uid
        uid = request.form.get("uid")
        pwd = request.form.get("pwd")
        
        if uid is not None and pwd is not None: # filled uid and pwd, check login
            reset = request.form.get("reset")
            if reset == "true" and users.check_user(uid) == -1: # pwd need reset
                users.change_pwd(uid, pwd)
                flash("Password reset success", "success")
                return render_template("login.html")

            if users.login(uid, pwd) == 1:
                session[users.SESSION_KEYNAME] = users.login_register(uid)
                if session[users.SESSION_KEYNAME]:
                    flash("Login success", "success")
                else:
                    flash("Login failed", "error")
                return redirect("/")
            elif users.check_user(uid) == -1:
                flash("User not exist", "warning")
                return render_template("login.html")
            else:
                flash("Password incorrect", "error")
                return render_template("login.html", uid=uid)

        # only filled uid, check user and ask for password
        uid_condition = users.check_user(uid)

        if uid_condition == 0: # user not exist
            flash("User not exist", "warning")
            return render_template("login.html")
        elif uid_condition == -1: # user pwd reseted
            return render_template("login.html", uid=uid, reset='true') # pwd need reset
        return render_template("login.html", uid=uid) # fill password
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    if users.logout(session.pop(users.SESSION_KEYNAME, None)):
        flash("Logout success", "success")
    else:
        flash("Logout failed", "error")
    return redirect("/")

@app.route("/cloud", methods=["GET"])
def cloud():
    addr = request.remote_addr
    uid = users.check_login(session)
    if not uid: # not login
        flash("Please login first", "warning")
        return redirect('/login')
    
    return render_template("cloud.html", uid=uid, addr=addr, base="", files=[
        {"name": "private", "file": False},
        {"name": "share", "file": False},
        {"name": "public", "file": False},
        {"name": "visit", "file": False}
        ], priviledge=False)

@app.route("/cloud/", methods=["GET"]) # redirect /cloud/ to /cloud
def cloud_():
    return redirect("/cloud")

@app.route("/cloud/<path:subpath>", methods=["GET"])
def cloud_browse(subpath):
    addr = request.remote_addr
    addr = request.remote_addr
    uid = users.check_login(session)
    if not uid: # not login
        flash("Please login first", "warning")
        return redirect('/login')
    
    tar_path = users.get_absPath(uid, subpath)
    if tar_path is None: # invalid path
        flash("Invalid path", "error")
        return redirect("/cloud")
    
    if tar_path == "visit": # visit path
        files = [{"name": one, "file": False} for one in users.get_users() if uid != one] # list all users

    elif os.path.isfile(tar_path): # is file, online preview
        file_type = utils.get_filetype(tar_path)
        if request.args.get("preview") == "true": # online preview (without page)
            return response.make_preview_response(tar_path, file_type)
        else: # online preview (with page)
            return render_template("preview.html", uid=uid, addr=addr, file=subpath, file_type=file_type,
                                   privilege=subpath.startswith("share") or subpath.startswith("public"))
    else:
        files = utils.list_dir(tar_path)

    return render_template("cloud.html", uid=uid, addr=addr, base=subpath, files=files,
                           privilege=not subpath.startswith("visit"))

@app.route("/download/<path:subpath>", methods=["GET"])
def download(subpath):
    uid = users.check_login(session)
    if not uid: # not login
        flash("Please login first", "warning")
        return redirect('/login')
    
    addr = request.remote_addr

    tar_path = users.get_absPath(uid, subpath)
    if tar_path is None: # invalid path
        flash("Invalid path", "error")
        return redirect("/cloud")

    print(f"File {subpath} download by {uid} from {addr}")
    return response.make_download_response(tar_path)
    
@app.route("/upload", methods=["POST"])
def upload():
    uid = users.check_login(session)
    if not uid: # not login
        flash("Please login first", "warning")
        return redirect('/login')
    
    addr = request.remote_addr
    base = request.form.get("base")

    file = request.files["file"]
    if not file: # no file selected
        flash("Please select a file", "warning")
        return redirect(f"/cloud/{base}")
    
    if file.content_length > FILE_MAXSIZE:
        flash(f"The file size exceeds the limit ({utils.convert_size(FILE_MAXSIZE)})", "error")
        return redirect(f"/cloud/{base}")
    
    file_path, file_name = utils.make_unique(users.get_absPath(uid, base), file.filename)
    file.save(file_path)
    flash(f"File {file_name} uploaded", "success")
    print(f"File {file_name} uploaded by {uid} from {addr}")
    return redirect(f"/cloud/{base}")

@app.route("/mkdir", methods=["POST"])
def mkdir():
    uid = users.check_login(session)
    if not uid: # not login
        return redirect('/login')
    
    base = request.form.get("base")
    new_dir = request.form.get("new_dir")

    if new_dir is None or new_dir == "":
        flash("Please input a directory name", "warning")
        return redirect(f"/cloud/{base}")
    
    new_dir = os.path.join(base, new_dir)
    new_dir_path = users.get_absPath(uid, new_dir)

    if os.path.exists(new_dir_path):
        flash(f"Directory {new_dir} already exists", "warning")
        return redirect(f"/cloud/{base}")
    try:
        os.mkdir(new_dir_path)
    except Exception:
        flash(f"Directory {new_dir} create failed", "error")
        return redirect(f"/cloud/{base}")
    
    print(f"Directory {new_dir} created by {uid}")
    flash(f"Directory {new_dir} created", "success")
    return redirect(f"/cloud/{base}")

@app.route("/share", methods=["GET", "POST"])
def share():
    addr = request.remote_addr

    if request.method == "GET": # using token to download shared file
        token = request.args.get("token")
        if token is None:
            flash("Share need token", "error")
            return redirect("/")
        token_value = security.get_key_value(token)
        if token_value is None or token_value[0] != "share":
            flash("Invalid token", "error")
            return redirect("/")
        tar_path = token_value[1]
        if tar_path is None: # invalid path
            flash("Invalid path", "error")
            return redirect("/")
        print(f"Shared file {tar_path} download by ip {addr}")
        return response.make_download_response(tar_path)
    
    else: # share file
        uid = users.check_login(session)
        if not uid: # not login
            flash("Please login first", "warning")
            return redirect('/login')
        
        file_path = request.form.get("share_file")
        tar_path = users.get_absPath(uid, file_path)
        if tar_path is None:
            flash("Invalid path", "error")
            return redirect("/cloud")
        token = security.make_key(tar_path, "share")
        url = f"{SERVER_ADDR}/share?token={token}"
        print(f"File {file_path} shared by {uid}")
        return render_template('share.html', url=url)


if __name__ == "__main__":
    print("Checking directories...")
    utils.check_workdir()
    security.check_workdir()
    users.check_workdir()
    print("Done.")
    print("Starting server")
    app.run(host=IP, port=PORT, debug=DEBUG)
    
