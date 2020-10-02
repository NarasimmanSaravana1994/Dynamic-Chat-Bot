from pymongo import MongoClient
from bson.json_util import dumps
import json

##### database connection #####


client = MongoClient('localhost', 27017)
db = client.test
session = db.get_collection('session')
question_flow = db.get_collection('question_flow')

##### database connection #####


def insert_collection(session_id):
    try:
        session.insert_one({"session_id": str(session_id),
                            "status": "True", "chat_flow": []})
        return True
    except Exception as ex:
        print("Error : ", ex)
        return False


def is_sessionid_exists(session_id):
    try:
        count = session.find({"session_id": session_id}).count()
        if count == 1:
            return True
        else:
            return False
    except Exception as ex:
        #print("Error : ", ex)
        return False


def get_value_with_session_id(session_id):
    try:
        value = session.find_one({"session_id": session_id}, {"_id": 0})
        value = json.loads(dumps(value))
        return value
    except Exception as ex:
        print("Error : ", ex)
        return {}

def chat_flow_session_update(session_id, chat_flow):
    try:

        # is_exit = session.find({"$and": [{"session_id": session_id}, {
        #                        "chat_flow.question_id": chat_flow['question_id']}]}).count()

        # if is_exit == 1:
        #     session.update({"$and": [{"session_id": session_id}, {"chat_flow.question_id": chat_flow['question_id']}]}, {
        #                    "$set": {"chat_flow.$.answer": chat_flow['answer']}})
        # else:
        session.update_one(
            {
                "session_id": str(session_id)},
            {
                "$push": {
                    "chat_flow": chat_flow
                }
            }
        )

    except Exception as ex:
        print("Error : ", ex)
        return False


def get_question_chat(company_id, domain_id):
    chat_flow = question_flow.find_one(
        {"company_id": company_id, "domain_id": domain_id})
    chat_flow = json.loads(dumps(chat_flow))
    return chat_flow
