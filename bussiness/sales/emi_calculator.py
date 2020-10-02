import numpy as np


def emi_calculation(loan_amount,tenture=5,interest_rate=15.00):
    monthly_emi =-1 * np.pmt(interest_rate / 12, tenture*12 ,int(loan_amount))
    return interest_rate,monthly_emi,tenture,loan_amount,2


def emi_calculation_sales(chat_history):
    amount = chat_history[8]['answer']
    return emi_calculation(amount)