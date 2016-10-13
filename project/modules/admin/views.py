import datetime
import unicodedata
import re
import os
import glob
import codecs
from contextlib import contextmanager
from flask import render_template, abort, request, redirect, url_for
from project import config
from project.database import db
from project.frontend import frontend
from project.util import rights_required, get_commission, has_rights
from project.modules.user.helpers import notify_user
from project.modules.constant import Constant, CommissionSettings
from project.modules.info import InfoPage
from project.modules.doer_application import DoerApplication
from project.modules.user.model import User

from .forms import *

def normalize_dash(c):
    if unicodedata.category(c) == 'Pd':
        return '-'
    return c

def normalize_dashes(s):
    return ''.join(normalize_dash(c) for c in s)

def normalize_commission_string(s):
    return normalize_dashes(s).strip().replace(',', '.')

@frontend.route('admin/settings/', methods=['GET', 'POST'])
@rights_required('admin')
def admin_settings():
    PRICE_UPPER_BOUND = 999999

    settingsForm = ChangeSettingsForm()

    commissions = CommissionSettings.query.all()
    commission_ranges_text = ''
    for comm in commissions:
        if comm.upper_bound == PRICE_UPPER_BOUND:
            commission_ranges_text += '{0:.0f}+ = {1:.2f}%'.format(float(comm.lower_bound), float(comm.commission))
        else:
            commission_ranges_text += '{0:.0f} - {1:.0f} = {2:.2f}%'.format(float(comm.lower_bound), float(comm.upper_bound), float(comm.commission*100))
        commission_ranges_text += '\n'

    if settingsForm.validate_on_submit():
        slogan = settingsForm.slogan.data
        seo_keywords = settingsForm.seo_keywords.data
        seo_description = settingsForm.seo_description.data

        commission_ranges = settingsForm.commission_ranges.data.splitlines()
        commission_ranges = [commission_range_string for commission_range_string in commission_ranges if commission_range_string.strip()]

        commission_settings = []
        reg = '(?:([0-9\.\,]+)\s*\-\s*([0-9\.\,]+)|([0-9\.\,]+\s*\++))\s*(?:\:|\=)\s*([0-9\.\,]+\%?)'
        for commission_range in commission_ranges:
            s = normalize_commission_string(commission_range)
            try:
                lower, upper, global_upper, commission = re.search(reg, s).groups()
                lower = int(lower) if lower else None
                upper = int(upper) if upper else None
                if global_upper:
                    if global_upper[-1] == '+': global_upper = global_upper[:-1]
                    global_upper = int(global_upper)
                if commission[-1] == '%':
                    commission = float(commission.strip('%')) / 100.0
                else:
                    commission = float(commission)
                if lower != None and lower > upper:
                    tmp = lower
                    lower = upper
                    upper = tmp
                commission_settings.append({
                    'lower': lower,
                    'upper': upper,
                    'commission': commission,
                    'global_upper': global_upper
                })
            except (AttributeError, ValueError):
                settingsForm.commission_ranges.errors.append('Диапазоны введены в неправильном формате. Пожалуйста, введите их в соответствии с инструкцией ниже.')
            else:
                try:
                    settings = Constant.query.filter_by(active=True).first()
                    settings.slogan = slogan
                    settings.seo_keywords = seo_keywords
                    settings.seo_description = seo_description

                    db.session.query(CommissionSettings).delete()
                    for setting in commission_settings:
                        if setting['lower'] == setting['upper'] == None:
                            db.session.add(
                                CommissionSettings(lower_bound=setting['global_upper'], upper_bound=PRICE_UPPER_BOUND, commission=setting['commission'])
                            )
                        else:
                            db.session.add(
                                CommissionSettings(lower_bound=setting['lower'], upper_bound=setting['upper'], commission=setting['commission'])
                            )
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    settingsForm.slogan.errors.append(str(e))

    return render_template('admin/settings.html', **{
        'settingsForm': settingsForm,
        'commission_ranges_text': commission_ranges_text
    })

@frontend.route('admin/categories/', methods=['GET'])
@rights_required('admin')
def admin_categories():
    

    return render_template('admin/categories.html', **{
        
    })

def letter_human_name(name):
    return {
        'welcome': 'Добро пожаловать',
        'got_doer_rights': 'Получены права исполнителя',
        'you_accepted_offer': 'Вы приняли предложение исполнителя',
        'your_offer_was_accepted': 'Ваше предложение принято',
        'restore_password': 'Восстановление пароля',
        'your_new_password': 'Пароль успешно восстановлен'
    }.get(name, name)

@frontend.route('admin/edit_letters/', methods=['GET'])
@rights_required('admin')
def admin_edit_letters():
    filenames = glob.glob('templates/letters/*.html')
    letters = []
    for filename in filenames:
        plain_name = os.path.splitext(os.path.basename(filename))[0]
        if plain_name == 'base':
            continue
        letters.append({
            'name': plain_name,
            'human_name': letter_human_name(plain_name)
        })


    return render_template('admin/edit_letters.html', **{
        'letters': letters
    })

@frontend.route('admin/edit_letter/<name>/', methods=['GET', 'POST'])
@rights_required('admin')
def admin_edit_letter(name):
    letter = {'name': name}
    with codecs.open('templates/letters/' + name + '.html', 'r', 'utf-8') as letter_file:
        letter['text'] = letter_file.read()

    form = LetterForm()

    if form.validate_on_submit():
        with codecs.open('templates/letters/' + name + '.html', 'w', 'utf-8') as letter_file:
            letter_file.write(form.text.data)
        with codecs.open('templates/letters/' + name + '.html', 'r', 'utf-8') as letter_file:
            letter['text'] = letter_file.read()

    return render_template('admin/edit_letter.html', **{
        'letterForm': form,
        'letter': letter
    })

def infoblock_human_name(name):
    return {
        'main_page_upper': 'Главная страница (верхний блок информации)',
        'main_page_lower': 'Главная страница (нижний блок информации)'
    }.get(name, name)

@frontend.route('admin/edit_infoblocks/', methods=['GET'])
@rights_required('admin')
def admin_edit_infoblocks():
    filenames = glob.glob('templates/infoblocks/*.html')
    infoblocks = []
    for filename in filenames:
        plain_name = os.path.splitext(os.path.basename(filename))[0]
        if plain_name.startswith('base_'):
            continue
        infoblocks.append({
            'name': plain_name,
            'human_name': infoblock_human_name(plain_name)
        })


    return render_template('admin/edit_infoblocks.html', **{
        'infoblocks': infoblocks
    })

@frontend.route('admin/edit_infoblock/<name>/', methods=['GET', 'POST'])
@rights_required('admin')
def admin_edit_infoblock(name):
    infoblock = {'name': name, 'human_name': infoblock_human_name(name)}
    with codecs.open('templates/infoblocks/' + name + '.html', 'r', 'utf-8') as infoblock_file:
        infoblock['text'] = infoblock_file.read()

    form = LetterForm()

    if form.validate_on_submit():
        with codecs.open('templates/infoblocks/' + name + '.html', 'w', 'utf-8') as infoblock_file:
            infoblock_file.write(form.text.data)
        with codecs.open('templates/infoblocks/' + name + '.html', 'r', 'utf-8') as infoblock_file:
            infoblock['text'] = infoblock_file.read()

    return render_template('admin/edit_infoblock.html', **{
        'infoblockForm': form,
        'infoblock': infoblock
    })

@frontend.route('admin/info/', methods=['GET'])
@rights_required('admin')
def admin_info():
    pages = InfoPage.query.all()
    
    return render_template('admin/info.html', **{
        'pages': pages
    })

@frontend.route('admin/applications/confirm/', methods=['POST'])
@rights_required('admin')
def confirm_doer_application():
    if 'application_id' not in request.form:
        pass
    application_id = request.form['application_id']
    application = DoerApplication.query.get(application_id)
    user = application.user
    # TODO error checking
    try:
        #user.doer = True
        #if not user.balance:
        #    user.balance = 0
        if not has_rights(user, 'trusted'):
            user.rights = 'trusted'
        db.session.delete(application)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    
    notify_user(user, {
        'email': render_template('letters/got_doer_rights.html')
    }, subject='Вы стали проверенным пользователем!')

    return redirect(url_for('frontend.admin_applications'))

@frontend.route('admin/applications/reject/', methods=['POST'])
@rights_required('admin')
def reject_doer_application():
    if 'application_id' not in request.form:
        pass
    application_id = request.form['application_id']
    application = DoerApplication.query.get(application_id)

    # TODO error checking
    if application:
        try:
            db.session.delete(application)
            db.session.commit()
        except:
            db.session.rollback()
            raise
    
    return redirect(url_for('frontend.admin_applications'))

@frontend.route('admin/applications/', methods=['GET'])
@rights_required('admin')
def admin_applications():
    applications = DoerApplication.query.all()

    # TODO
    return render_template('admin/applications.html', **{
        'applications': applications
    })


@frontend.route('admin/users/', methods=['GET'])
@rights_required('admin')
def admin_users():
    return render_template('admin/users.html', **{
        'all_users': User.query.filter_by(deleted=False).all()
    })