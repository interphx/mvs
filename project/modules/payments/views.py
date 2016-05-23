from flask import request, render_template
from sqlalchemy.orm.exc import MultipleResultsFound
from project.frontend import frontend
from project import db
from urllib.parse import urlencode
from project.util import rights_required
from flask.ext.login import current_user

from .model import Payment

# TODO: WMI_ERROR helper
def wmi_error(text):
	return 'WMI_RESULT=RETRY&' + urlencode({'WMI_DESCRIPTION': text})

# TODO: Confirm hash
@frontend.route('payments/confirm/', methods=['POST'])
def confirm_payment():
	if ('WMI_ORDER_STATE' not in request.form):
		return wmi_error('Отсутствует параметр WMI_ORDER_STATE')
	if ('WMI_PAYMENT_NO' not in request.form):
		return  wmi_error('Отсутствует параметр WMI_PAYMENT_NO')
	if ('WMI_PAYMENT_AMOUNT' not in request.form):
		return  wmi_error('Отсутствует параметр WMI_PAYMENT_AMOUNT')

	order_state = request.form.get('WMI_ORDER_STATE', None)

	if order_state.lower() != 'accepted':
		return  wmi_error('WMI_ORDER_STATE не равен Accepted (' + str(order_state) + ')')

	payment_id = request.form.get('WMI_PAYMENT_NO', None)
	payment_amount_string = request.form.get('WMI_PAYMENT_AMOUNT', None).strip()
	try:
		payment_amount = int(float(payment_amount_string.replace(',', '.')))
	except:
		return  wmi_error('Некоррекнтый параметр WMI_PAYMENT_AMOUNT (' + str(payment_amount_string) + ')')
	# ID уникален
	payment = Payment.query.filter_by(id=int(payment_id), done=False).first()
	if not payment:
		return  wmi_error('Неверный номер платежа: ' + str(payment_id))
	user = payment.user
	try:
		payment.done = True
		# TODO?
		db.session.delete(payment)
		user.balance += payment_amount
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		return  wmi_error('Ошибка БД: ' + str(e))
	return 'WMI_RESULT=OK'


@frontend.route('payments/new/', methods=['GET', 'POST'])
@rights_required('user')
def payment_new():
	payment = Payment(user_id=current_user.id)
	try:
		db.session.add(payment)
		db.session.commit()
	except:
		db.session.rollback()
		raise
	return render_template('payments/new.html', **{
		'payment_id': payment.id
	})

@frontend.route('payments/success/', methods=['GET', 'POST'])
def payment_success():
	# TODO: Display additional data?
	return render_template('payments/success.html')

@frontend.route('payments/fail/', methods=['GET', 'POST'])
def payment_fail():
	# TODO: Display additional data?
	return render_template('payments/fail.html')