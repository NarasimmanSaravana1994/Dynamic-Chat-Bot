from flask import Flask, request, jsonify, Response, make_response, send_file, send_from_directory
from flask_cors import CORS
from flask_api import status
from flask_restless import APIManager
import flask_monitoringdashboard as dashboard
import pandas as pd
import json
import datetime
import os
from io import BytesIO
import csv
from database_util import db
from bussiness import bussiness
import requests

# import sqlite3
# from sqlite3 import Error.

app = Flask(__name__)
#app.config['JSON_SORT_KEYS'] = False
CORS(app, resources={r"/*": {"origins": "*"}})
#dashboard.bind(app)


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


@app.route('/v1/test/')
def index():
	return "Chat api flask is working !"


@app.route('/v1/chat/', methods=['POST'])
def login_flow():

    chat_responce = {"question": "", "question_type": "", "input_type": ""}

    request_data = json.loads(request.data.decode(), strict=False)
    session_id = str(request_data['sessionid']).strip()

    if request_data['companyid'].strip() != "":
        company_id = int(request_data['companyid'].strip())
    else:
        company_id = 0

    if request_data['domainid'].strip() != "":
        domain_id = int(request_data['domainid'].strip())
    else:
        domain_id = 0

    if request_data['questionid'] != "":
        question_id = request_data['questionid']
    else:
        question_id = 0

    user_chat = str(request_data['userchat']).strip()

    if not db.is_sessionid_exists(session_id):
        db.insert_collection(session_id)

        chat_responce = bussiness.question_generation(
            1, company_id, domain_id, True)
        return jsonify(chat_responce)
    else:
        if user_chat == "":
            return "Please enter the value..."
        else:
            bussiness.chat_session_update(
                session_id, company_id, domain_id, question_id, user_chat)
            final_reponce = bussiness.chat_responce(
                session_id, company_id, domain_id)
            return final_reponce

@app.route('/v1/fileupload/', methods=['POST'])
def fileupload():
    sessionid = request.form['sessoin_id']
    name = request.files['file'].filename
    file = request.files['file']

    path = '/home/administrator/AI_PROJECTS/CHATBOT_demo_13_07_2020/uploaded_file/'+sessionid
    if not os.path.exists(path):
        os.mkdir(path)
        file.save(path+"/"+name)
    else:
        file.save(path+"/"+name)

    return path+"/"+name

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4005, threaded=True)
