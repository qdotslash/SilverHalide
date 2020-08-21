import os
import logging
from datetime import datetime
from flask import Flask, request, render_template, url_for
from flask_json import FlaskJSON, JsonError, json_response, as_json
from pprint import pformat as pf

import app_utils_s3
import config_s3

sitename = config_s3.py['sitename']

app = Flask(__name__)
app.config.from_object(__name__)
FlaskJSON(app)


@app.route('/get_time')
def get_time():
    now = datetime.utcnow()
    return json_response(time=now)


@app.route('/')
def init():
    return render_template('index_s3.html', sitename=sitename)


@app.route('/fileList/<path:get_path>', methods=['GET'])
@as_json
def get_file_list(get_path):
    file_list = app_utils_s3.get_s3_file_list(get_path)
    return(file_list)


@app.route('/init', methods=['GET'])
@app.route('/<path:scan_dir>', methods=['GET'])
@as_json
def get_dirs(scan_dir="/"):

    # construct path
    p = config_s3.py['mediadir'] + scan_dir
    # handle trailng slash
    if not p.endswith('/'):
        p = p + '/'
    elif p.endswith('//'):
        p = p[:-1]
    dir_tree_key = scan_dir[:-1]
    print('scan_dir p: ' + p)
    print('dir tree key: ' + dir_tree_key)

    # scan dir for files and subdirs
    dir_list = app_utils_s3.get_s3_sub_dirs(root_dir=p)

    return(dir_list)


@app.route('/creds')
@as_json
def get_creds():
    creds = app_utils_s3.return_creds(config_s3.py['assume_role'])
    print(creds)
    return(creds)


@app.route('/get_value')
@as_json
def get_value():
    return dict(value=12)


@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='favicon.ico')


if __name__ == '__main__':
    app.debug = True
    app.run('10.242.46.27', port='8080')

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/': os.path.join(os.path.dirname(__file__), 'static')
    })
