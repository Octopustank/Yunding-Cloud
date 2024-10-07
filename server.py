from flask import Flask, render_template, request, redirect, send_file, flash, session, make_response
import datetime as dt
import os
from urllib.parse import quote
import time as tm
import markdown

import utils
import users

IP = "0.0.0.0"
PORT = 5000

FILE_MAXSIZE = 5 * 1024 * 1024 * 1024 # file max size 5GB

app = Flask("Cloud")
app.config['JSON_AS_ASCII'] = False
app.secret_key = "very-hard-to-guess-string"

@app.route("/")
def index():
    addr = request.remote_addr
    uid = session.get("account")
    if uid is None: # not login
        return redirect('/login')
    else: # already login
        return render_template("index.html", uid=uid, addr=addr)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("account") is not None: # already login
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

            if users.check_login(uid, pwd) == 1:
                session["account"] = uid
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
    session.pop("account", None)
    return redirect("/login")

@app.route("/cloud", methods=["GET"])
def cloud():
    addr = request.remote_addr
    uid = session.get("account")
    if uid is None: # not login
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
    uid = session.get("account")
    if uid is None: # not login
        return redirect('/login')
    
    tar_path = users.get_absPath(uid, subpath)
    if tar_path is None: # invalid path
        flash("Invalid path", "error")
        return redirect("/cloud")
    
    if tar_path == "visit": # visit path
        files = [{"name": uid, "file": False} for uid in users.get_users()] # list all users

    elif os.path.isfile(tar_path): # is file, online preview
        file_type = utils.get_filetype(tar_path)
        if request.args.get("preview") == "true": # online preview (without page)
            return utils.make_preview_response(tar_path, file_type)
        else: # online preview (with page)
            return render_template("preview.html", uid=uid, addr=addr, file=subpath, file_type=file_type)
    else:
        files = utils.list_dir(tar_path)

    return render_template("cloud.html", uid=uid, addr=addr, base=subpath, files=files,
                           priviledge=not subpath.startswith("visit"))

@app.route("/download/<path:subpath>", methods=["GET"])
def download(subpath):
    addr = request.remote_addr
    uid = session.get("account")
    if uid is None: # not login
        return redirect('/login')
    
    tar_path = users.get_absPath(uid, subpath)
    if tar_path is None: # invalid path
        return redirect("/cloud")

    return utils.make_download_response(tar_path)
    
@app.route("/upload", methods=["POST"])
def upload():
    addr = request.remote_addr
    uid = session.get("account")
    base = request.form.get("base")
    if uid is None: # not login
        return redirect('/login')

    file = request.files["file"]
    if not file: # no file selected
        flash("Please select a file", "warning")
        return redirect(f"/cloud/{base}")
    
    if file.content_length > FILE_MAXSIZE:
        flash(f"The file size exceeds the limit ({utils.humanize_bytes(FILE_MAXSIZE)})", "error")
        return redirect(f"/cloud/{base}")
    
    file_path, file_name = utils.make_unique(users.get_absPath(uid, base), file.filename)
    file.save(file_path)
    flash(f"File {file_name} uploaded", "success")
    return redirect(f"/cloud/{base}")

@app.route("/mkdir", methods=["POST"])
def mkdir():
    uid = session.get("account")
    base = request.form.get("base")
    new_dir = request.form.get("new_dir")
    if uid is None: # not login
        return redirect('/login')
    
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
    
    flash(f"Directory {new_dir} created", "success")
    return redirect(f"/cloud/{base}")

if __name__ == "__main__":
    app.run(host=IP, port=PORT, debug=True)
