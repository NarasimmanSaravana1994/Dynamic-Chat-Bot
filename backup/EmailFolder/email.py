from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from database_util import db


me = "info@easeroom.com"
my_password = "Ease*4321"
#my_password = "%Tgbyui9"
#to = ["narasimman.s@armsoft-tech.com"]
to = ["cms@easeroom.com"]

html_string = '''<html><body><div>Hi team </div><div>Please refer below mentioned chat history  </div> <br/> {} <br/><div>Thanks & Regards </div><div>Easeroom Support </div></body></html>'''


def email_sending(chat_session_id, company_id, domain_id):
	chat_json = (db.get_value_with_session_id(chat_session_id))
	chat_history = chat_json['chat_flow']

	chat_questions = db.get_question_chat(company_id, domain_id)['questions']

	questions = []
	answers = []

	for index,value in enumerate(chat_history):
		question_id = int(value["question_id"])
		answer = value["answer"]
		for index_1,value_1 in enumerate(chat_questions):
			if value_1["question_id"] == question_id:
				questions.append(value_1["question"])
				answers.append(answer)
				break
	
	html = "<div> Question : {} </div>  <div> Answer : {} </div>"
	final_html = ""
	for index,value in enumerate(questions):
		string = html.format(value.replace("\n",""),answers[index])
		final_html = final_html + string +"  "


	mail_html_content = html_string.format(final_html)


	msg = MIMEMultipart()
	msg['Subject'] = "REG : Chat history..."

	msg['From'] = me
	msg['To'] = ",".join(to)
	ctype = None
	if ctype is None or encoding is not None:
		ctype = "application/octet-stream"

		maintype, subtype = ctype.split("/", 1)
		text = MIMEText(mail_html_content, 'html')
		msg.attach(text)
		s = smtplib.SMTP('smtp.zoho.com', 587,)
		s.starttls()
		s.login(me, my_password)

		s.sendmail(me, to, msg.as_string())
		s.quit()

	return True 
