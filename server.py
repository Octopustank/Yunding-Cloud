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
        {"name": "private", "size": "", "file": False},
        {"name": "share", "size": "", "file": False},
        {"name": "public", "size": "", "file": False}
        ])

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
        return redirect("/cloud")

    if os.path.isfile(tar_path): # is file, online preview
        file_type = utils.get_filetype(tar_path)
        if request.args.get("preview") == "true": # online preview (without page)
            return utils.make_preview_response(tar_path, file_type)
        else: # online preview (with page)
            return render_template("preview.html", uid=uid, addr=addr, file=subpath, file_type=file_type)
    
    files = utils.list_dir(tar_path)

    return render_template("cloud.html", uid=uid, addr=addr, base=subpath, files=files)

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
    
    

if __name__ == "__main__":
    app.run(host=IP, port=PORT, debug=True)
