import re
import os
import os.path
import datetime
import functools
from urllib.parse import quote_plus, urlparse, urljoin
from flask import request, url_for, redirect
from unidecode import unidecode
from flask.ext.login import current_user
from project.utils import json

def normalize_mobile(phone_string):
    """
    Приведение мобильных к международному формату (только Россия!)
    """
    # Последние 10 цифр, найденные в строке
    if phone_string[:2] == '+7': phone_string = phone_string[2:]
    raw_number = ''.join(c for c in phone_string if c.isdigit())[-10:]
    return '+7' + raw_number


def get_commission(task_price):
    import project.modules.constant
    min_commission = project.modules.constant.Constant.query.filter_by(active=True).first().min_commission
    settings = project.modules.constant.CommissionSettings.query \
        .filter(project.modules.constant.CommissionSettings.lower_bound <= task_price) \
        .filter(project.modules.constant.CommissionSettings.upper_bound >= task_price).first()
    if not settings:
        raise Exception('Не найден подходящий диапазон комиссии для цены в {0} руб.'.format(task_price))
    commission_coeff = settings.commission
    result = int(float(task_price) * commission_coeff)
    return max(min_commission, result)

def get_redirect_url(form, fallback=0):
    '''
    Checks form and request for redirect_to field or arg respectively.
    URL must be from the same domain.
    '''
    if 'redirect_to' in form.data and is_safe_url(form.redirect_to.data):
        return form.redirect_to.data
    elif 'redirect_to' in request.args and is_safe_url(request.args.get('redirect_to')):
        return request.args.get('redirect_to')
    elif fallback == 0:
        return url_for('frontend.index')

    return fallback
    
rights_order = ['guest', 'deleted', 'user', 'trusted', 'moderator', 'admin']
def has_rights(user, rights):
    rights_level = user.rights or 'guest'
    if rights_level not in rights_order or rights not in rights_order:
        return False
    if rights_order.index(rights_level) < rights_order.index(rights):
        return False
    return True

def rights_required(rights):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not has_rights(current_user, rights):
                return redirect( url_for('frontend.access_denied') )
            return f(*args, **kwargs)
        return wrapper
    return decorator

def api_rights_required(rights):
    rights_order = ['guest', 'user', 'moderator', 'admin']
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            rights_level = current_user.rights or 'guest'
            if rights_level not in rights_order:
                return {"message": "Permission denied"}, 403
            if rights_order.index(rights_level) < rights_order.index(rights):
                return {"message": "Permission denied"}, 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

def api_login_required(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated():
            return {"message": "Login required"}, 302
        return f(*args, **kwargs)
    
    return wrapper

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

def getOrCreate(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        return instance

def createIfNone(session, model, **kwargs):
    getOrCreate(session, model, **kwargs)

def getImmediateSubdirectories(path):
    return [name for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))]

def mergeDicts(a, b):
    if isinstance(a,dict) and isinstance(b,dict):
        for k,v in b.items():
            if k not in a:
                a[k] = v
            else:
                a[k] = mergeDicts(a[k],v)
    return a

def urlify(s):
    s = unidecode(s)
    s = s.replace("'", '')
    s = re.sub(r"\s+", '-', s)
    s = s.lower()
    return quote_plus( s )