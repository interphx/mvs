from project import app
from flask.ext.mail import Mail, Message

# Манкипатч, в последней версии плагина ещё не пофиксили проблемы с кодировкой.
# Без этого тема письма будет отображаться без пробелов.
import flask.ext.mail
flask.ext.mail.message_policy = None

mail = Mail(app)

def send_mail(subject, body, sender, recipients, html=''):
	with app.app_context():
		msg = Message(subject, sender=sender, recipients=recipients)
		msg.html = html
		msg.body = body
		mail.send(msg)