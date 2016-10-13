import datetime
import re
from project import app, config
from project.util import get_commission, has_rights
from project.modules.constant import Constant
from jinja2 import Markup

app.jinja_env.globals['config'] = config

@app.template_filter('plural_form')
def plural_form(num, cases):
	'''
	num -- число
	cases -- [именительный, родительный, предложный]
	'''
	num = abs(num)
	reslut = cases[0]
	if str(num).find('.') >= 0:
		return cases[1]
	else:
		if (num % 10 == 1) and (num % 100 != 11):
			return cases[0]
		elif (num % 10 >= 2) and (num % 10 <= 4) and (num % 100 < 10 or num % 100 >= 20):
			return cases[1]
		else:
			return cases[2]

@app.template_filter('datetime_pretty')
def datetime_pretty(dt):
	return dt.strftime('%d.%m.%Y %H:%M')

@app.template_filter('to_right_timezone')
def to_right_timezone(utc_dt):
	# Yekaterinburg time zone
	yekaterinburg = datetime.timedelta(hours=6)
	result = utc_dt + yekaterinburg
	return result

@app.template_filter('time_delta_text')
def time_delta_text(delta):
	result = ''
	days = delta.days
	hours, remainder = divmod(delta.seconds, 3600)
	minutes, seconds = divmod(remainder, 60)

	if days > 0:
		result += '{} {} '.format(str(days), plural_form(days, ['день', 'дня', 'дней']))
	if hours > 0:
		result += '{} {} '.format(str(hours), plural_form(hours, ['час', 'часа', 'часов']))
	result += '{} {} '.format(str(minutes), plural_form(minutes, ['минута', 'минуты', 'минут']))
	result += '{} {} '.format(str(seconds), plural_form(minutes, ['секунда', 'секунды', 'секунд']))
	return result

@app.template_filter('task_status_text')
def task_status_text(status):
	if status == 'created': return 'Поиск исполнителя'
	if status == 'assigned': return 'Назначено, выполняется'
	if status == 'completed': return 'Выполнено'
	return '???'

@app.template_filter('commission')
def commission(price):
	return get_commission(price)

@app.template_filter('nl2br')
def nl2br(value):
    value = re.sub(r'\r\n|\r|\n', '\n', value)
    return Markup(value.replace('\n', '<br />'))

@app.template_filter('oneline')
def oneline(value):
    value = re.sub(r'\r\n|\r|\n', '\n', value)
    return Markup(value.replace('\n', ' '))

@app.template_filter('rights_level_russian')
def rights_level_russian(rights_level_string):
    s = rights_level_string.strip().lower()
    if s == 'guest': return 'Гость'
    if s == 'user': return 'Пользователь'
    if s == 'moderator': return 'Модератор'
    if s == 'admin': return 'Администратор'
    return rights_level_string

def user_avatar_link(user):
    if user.avatar:
        return user.avatar.url
    else:
        return '/static/assets/img/no_avatar.png'

@app.context_processor
def inject_globals():
	return {
		'now': datetime.datetime.now(),
		'settings': Constant.query.filter_by(active=True).first(),
		'config': config,
        'user_avatar_link': user_avatar_link,
        'has_rights': has_rights
	}