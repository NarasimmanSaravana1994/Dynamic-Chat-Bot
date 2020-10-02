from database_util import db
from EmailFolder import email
import json
import requests
import re
from threading import Thread

class custom_error(Exception):
   """API connection failed ......"""
   pass


class Email_triggering(Thread):
    def __init__(self, session_id, company_id, domain_id):
        Thread.__init__(self)
        self.session_id = session_id
        self.company_id = company_id
        self.domain_id = domain_id

    def run(self):
        email.email_sending(self.session_id, self.company_id, self.domain_id)


def chat_session_update(session_id, company_id, domain_id, question_id, answer):
    insert_value = {}
    insert_value['company_id'] = company_id
    insert_value['domain_id'] = domain_id
    insert_value['question_id'] = question_id
    insert_value['answer'] = answer
    db.chat_flow_session_update(session_id, insert_value)
    return True


def chat_responce(session_id, company_id, domain_id, inital_flow=False):

    chat_json = (db.get_value_with_session_id(session_id))
    chat_history = chat_json['chat_flow']

    question_id = chat_history[-1]['question_id']
    answer = chat_history[-1]['answer']

    is_answer_checked, next_question = answer_verification(
        question_id, answer, company_id, domain_id)

    if is_answer_checked:
       chat_responce = question_generation(
           next_question, company_id, domain_id, chat_history)
    else:
        chat_responce = question_generation(
            question_id, company_id, domain_id, chat_history)

    # if question_id == 1:
    #     chat_responce['question'] = str(
    #         chat_responce['question']).format(answer)
    # if next_question == 5 or next_question == 6:
    #     chat_responce['question'] = str(
    #         chat_responce['question']).format(chat_responce["option_answers"])

    chat_responce = question_format(chat_responce, chat_history)

    if chat_responce["flow_end"]:
        thread_a = Email_triggering(session_id, company_id, domain_id)
        thread_a.start()

    return chat_responce

def question_format(chat_responce, chat_history):
    try:
        regex = r"\{(.*?)\}"
        matches = re.findall(regex, chat_responce["question"])
        matches = [int(i) for i in matches]
        for val in matches:
            manipulate_iteration = chat_responce["question"].replace(
                "{"+str(val)+"}", chat_history[val-1]['answer'])
            chat_responce["question"] = manipulate_iteration
    except:
        return chat_responce
     
    return chat_responce


def question_generation(question_id, company_id, domain_id, answer):
    chat_responces = {"question": "", "question_id": "",
                      "input_type": "", "flow_end": "","link":""}
    chat_questions = db.get_question_chat(
        company_id, domain_id)['questions']

    chat_responce = question_flow_identification(
        chat_questions, question_id)

    if chat_responce['is_db_provider']:
        answers = another_request_provider(chat_responce, answer)

        if chat_responce['flow_end'] == True:

            if company_id == 1 and domain_id == 1:
                HotelCode = answer[2]['answer']
                CheckinDate = str(answer[3]['answer'].split("~")[
                                  0]).replace("/", "-")
                CheckoutDate = str(answer[3]['answer'].split("~")[
                                   1]).replace("/", "-")

                chat_responces["question"] = chat_responce['question']
                chat_responces["link"] = str(chat_responce['link']).format(HotelCode, CheckinDate, CheckoutDate)

            elif company_id == 2 and domain_id == 1:
                HotelCode = "1110"
                CheckinDate = str(answer[3]['answer'].split("~")[
                                  0]).replace("/", "-")
                CheckoutDate = str(answer[3]['answer'].split("~")[
                                   1]).replace("/", "-")
                chat_responces["question"] = str(chat_responce['question']).format(
                    answers)
                
                chat_responces["link"] = str(chat_responce['link']).format(HotelCode, CheckinDate, CheckoutDate)

        else:
            chat_responces["question"] = chat_responce['question']
            chat_responces["link"] = chat_responce['link']

        chat_responces["question_id"] = chat_responce['question_id']
        chat_responces["input_type"] = chat_responce['input_type']
        chat_responces["flow_end"] = chat_responce['flow_end']        
        chat_responces["option_answers"] = answers        
    else:
        if chat_responce['flow_end'] == True:

            if company_id == 1 and domain_id == 1:
                HotelCode = answer[2]['answer']
                CheckinDate = str(answer[3]['answer'].split("~")[
                                  0]).replace("/", "-")
                CheckoutDate = str(answer[3]['answer'].split("~")[
                                   1]).replace("/", "-")

                chat_responces["question"] = chat_responce['question']
                chat_responces["link"] = str(chat_responce['link']).format(HotelCode, CheckinDate, CheckoutDate)
            elif company_id == 2 and domain_id == 1:
                HotelCode = "1110"
                CheckinDate = str(answer[3]['answer'].split("~")[
                                  0]).replace("/", "-")
                CheckoutDate = str(answer[3]['answer'].split("~")[
                                   1]).replace("/", "-")
                chat_responces["question"] = str(chat_responce['question']).format(
                    chat_responce["option_answers"])
                
                chat_responces["link"] = str(chat_responce['link']).format(HotelCode, CheckinDate, CheckoutDate)
        else:
            chat_responces["question"] = chat_responce['question']
            chat_responces["link"] = chat_responce['link']

        chat_responces["question_id"] = chat_responce['question_id']
        chat_responces["input_type"] = chat_responce['input_type']
        chat_responces["flow_end"] = chat_responce['flow_end']
        chat_responces["option_answers"] = chat_responce['option_answers']

    return chat_responces


def another_request_provider(provider_details, chat_history):

    provider_detail = provider_details["provider_details"]
    user_answer = answer = chat_history[-1]['answer']

    provider_name = provider_detail["provider_name"]

    if provider_name == "golden":
        gorup_id = '41'
    elif provider_name == "nk":
        gorup_id = '1'

    response = {}
    final_responce = []
    if provider_detail["method"] == "GET":
        if provider_detail["api_id"] == 1:
            response = requests.get(
                provider_detail["url"],
                headers=provider_detail["headers"],
            )

    elif provider_detail["method"] == "POST":
        if provider_detail["api_id"] == 2:
            response = requests.post(provider_detail["url"],
                                     headers=provider_detail["headers"],
                                     data={'GroupId': gorup_id, 'CityName': str(user_answer)})
        elif provider_detail["api_id"] == 3:
            data = []

            if provider_name == "golden":
                HotelCode = chat_history[2]['answer']
                CheckinDate = chat_history[3]['answer'].split("~")[0]
                CheckoutDate = chat_history[3]['answer'].split("~")[1]
                NoofAdults = chat_history[4]['answer']
            elif provider_name == "nk":
                HotelCode = provider_detail["request"]["HotelCode"]
                CheckinDate = chat_history[3]['answer'].split("~")[0]
                CheckoutDate = chat_history[3]['answer'].split("~")[1]
                NoofAdults = chat_history[4]['answer']
            #################################

            response = requests.post(provider_detail["url"],
                                     headers=provider_detail["headers"],
                                     data={'GroupId': gorup_id,
                                           'HotelCode': str(HotelCode),
                                           'CheckinDate': str(CheckinDate),
                                           'CheckoutDate': str(CheckoutDate),
                                           'NoofAdults': int(NoofAdults)})

    if response.status_code == 200:
        on_response = response.json()
        if provider_detail["provider_name"] == "golden":
            if provider_detail["api_id"] == 1:
                return on_response["CityNames"]
            elif provider_detail["api_id"] == 2:
                dict = {}
                for index, value in enumerate(on_response):
                    dict["hotel_code"] = value["HotelCode"]
                    dict["hotel_name"] = value["HotelName"]
                    final_responce.append(dict)
                    dict = {}
                return final_responce
            elif provider_detail["api_id"] == 3:
                return on_response["BestRate"]

        elif provider_detail["provider_name"] == "nk":
            if provider_detail["api_id"] == 1:
                return on_response["CityNames"]
            elif provider_detail["api_id"] == 2:
                dict = {}
                for index, value in enumerate(on_response):
                    dict["hotel_code"] = value["HotelCode"]
                    dict["hotel_name"] = value["HotelName"]
                    final_responce.append(dict)
                    dict = {}
                return final_responce
            elif provider_detail["api_id"] == 3:
                return on_response["BestRate"]
    else:
        pass


def question_flow_identification(question_array, question_id):

    chat_responce = []
    for index, value in enumerate(question_array):

        if value['question_id'] == question_id:
            chat_responce = value
            break

    return chat_responce


def answer_verification(question_id, answer, company_id, domain_id,):
    chat_questions = db.get_question_chat(
        company_id, domain_id)['questions']

    actual_answers = []
    mapped_question_id = 0
    is_db_provider = False

    for index, value in enumerate(chat_questions):
        if value['question_id'] == question_id:
            actual_answers = value['answers']
            mapped_question_id = value['next_question_id'][0]
            is_db_provider = value["is_db_provider"]
            break

    if is_db_provider:
        return True, mapped_question_id
    else:
        if len(actual_answers) == 0:
            return True, mapped_question_id
        else:
            for index, actual_answer in enumerate(actual_answers):
                if answer in actual_answer["answer"]:
                    return True, actual_answer["mapped_question_id"]

            return False, 0
