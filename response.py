import os
from flask import make_response, send_file, Response
import markdown
from urllib.parse import quote


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
    elif file_type == "html":
        with open(file_path, 'r', encoding="utf-8") as f:
            response = make_response(f.read())
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