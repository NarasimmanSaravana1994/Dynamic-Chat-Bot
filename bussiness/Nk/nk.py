import requests


def nk_provoider(provider_detail, chat_history):

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
            NoofAdults = 0
            HotelCode = ""
            CheckinDate_checkout = ""

            for val in chat_history:
                if val["question_id"] == 3:
                    HotelCode = val["answer"]
                if val["question_id"] == 4:
                    CheckinDate_checkout = val["answer"]
                if val["question_id"] == 5:
                    CheckinDate_checkout = val["answer"]
                if val["question_id"] == 6:
                    NoofAdults = val["answer"]

            HotelCode = HotelCode
            CheckinDate_ = CheckinDate_checkout.split(
                    "~")[0].replace("/", "-")
            CheckinDate__ = CheckinDate_.split("-")
            CheckinDate__[0] = CheckinDate_.split("-")[2]
            CheckinDate__[2] = CheckinDate_.split("-")[0]
            CheckinDate = "-".join(CheckinDate__)

            CheckoutDate_ = CheckinDate_checkout.split(
                    "~")[1].replace("/", "-")
            CheckoutDate__ = CheckoutDate_.split("-")
            CheckoutDate__[0] = CheckoutDate_.split("-")[2]
            CheckoutDate__[2] = CheckoutDate_.split("-")[0]
            CheckoutDate = "-".join(CheckoutDate__)
            NoofAdults = NoofAdults

            response = requests.post(provider_detail["url"],
                                            headers=provider_detail["headers"],
                                            data={'GroupId': gorup_id,
                                                'HotelCode': str(HotelCode),
                                                'CheckinDate': str(CheckinDate),
                                                'CheckoutDate': str(CheckoutDate),
                                                'NoofAdults': int(NoofAdults)})

    if response.status_code == 200:
        on_response = response.json()
        if provider_detail["api_id"] == 1:
            return "", on_response["CityNames"], False, False
        elif provider_detail["api_id"] == 2:
            dict = {}
            for index, value in enumerate(on_response):
                dict["hotel_code"] = value["HotelCode"]
                dict["hotel_name"] = value["HotelName"]
                final_responce.append(dict)
                dict = {}
            return "", final_responce, False, False
        elif provider_detail["api_id"] == 3 or provider_detail["api_id"] == 4:
                #return on_response["BestRate"],False
            return on_response["RoomTypeName"], on_response["BestRate"], on_response["Availability"], True

    else:
        print("Other provider Request fail...")
        return "", "",False,False
