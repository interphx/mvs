import project.smsru
from project.smsru import NotConfigured, WrongKey, InternalError, Unavailable

sms_client = project.smsru.Client()

def check_balance():
	return sms_client.balance()

def send_sms(phone, text, test=False):
	return sms_client.send(to=phone, message=text, test=test)