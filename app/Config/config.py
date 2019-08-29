from flask import Flask, request, Response, jsonify, current_app, abort, send_from_directory
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from functools import wraps
from datetime import datetime, timedelta, date
import requests
import base64
import json
import jwt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE , formatdate

app = Flask(__name__)
# ----------------for not sort key when send by JSONTIFY
app.config['JSON_SORT_KEYS'] = False
# ------------------------------------------------------
CORS(app)



# ------------------------------------------------------
# app.config['MYSQL_DATABASE_USER'] = "root"
# app.config['MYSQL_DATABASE_PASSWORD'] = "vpjk.shCyo8bf"
# app.config['MYSQL_DATABASE_DB'] = 'bookingroom_chat'
# app.config['MYSQL_DATABASE_HOST'] = '203.154.135.19'

# ------------------------------------------------------
# app.config['MYSQL_DATABASE_USER'] = "root"
# app.config['MYSQL_DATABASE_PASSWORD'] = ""
# app.config['MYSQL_DATABASE_DB'] = 'bookingroom_chat'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# ------------------------------------------------------
app.config['MYSQL_DATABASE_USER'] = "root"
app.config['MYSQL_DATABASE_PASSWORD'] = "l^9i@xib,kIlkily,ryoTN"
app.config['MYSQL_DATABASE_DB'] = 'bookingroom_db'
app.config['MYSQL_DATABASE_HOST'] = '203.150.57.159'

# ------------------------------------------------------
# app.config['MYSQL_DATABASE_USER'] = "root"
# app.config['MYSQL_DATABASE_PASSWORD'] = ""
# app.config['MYSQL_DATABASE_DB'] = 'meeting-room'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)


def connect_sql():
    def wrap(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                connection = mysql.connect()
                cursor = connection.cursor()
                return_val = fn(cursor, *args, **kwargs)
            finally:
                connection.commit()
                connection.close()
            return return_val
        return wrapper
    return wrap


def send_success(data):
    result = {'status': 200, 'msg': 'ok', 'data': data}
    return result


def toJson(data, columns):
    results = []
    for row in data:
        results.append(dict(zip(columns, row)))
    return results


def toJsonObject(data, columns):
    result = dict(zip(columns, data))
    return result


def json_response(messages=None, status=None, headers=None):
    if headers == None:
        headers = dict()
    headers.update({"Content-Type": "application/json"})
    contents = json.dumps(messages).replace('\'', '"')
    if(status == None):
        status = 200
    resp = Response(response=contents, headers=headers, status=int(status))
    return resp
