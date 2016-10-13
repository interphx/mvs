import random
import hashlib
import requests
import datetime as dt
from flask import render_template, redirect, url_for, abort, request
from flask.ext.login import logout_user, current_user
from project import app
from project.frontend import frontend
from project.util import get_redirect_target, redirect_back, get_redirect_url, normalize_mobile, rights_required
import project.sms as sms
import project.mail as mail
from project import db, config

from .forms import *
from .model import User, UloginData
from .helpers import create_user, login_user, InvalidEmailException, InvalidPasswordException, EmailExistsException, login_user_object, set_user_password
from .passgen import gen_password

from project.modules.mobile_confirmation import MobileConfirmation
from project.modules.category import Category
from project.modules.user_comment import UserComment
from project.modules.doer_application import DoerApplication
from project.modules.upload.helpers import upload_file, FileTypeNotAllowed
from project.modules.upload import Upload

@frontend.route('users/', methods=['GET'])
@frontend.route('users/doers/<category_name>/', methods=['GET'])
def user_list(category_name='all'):
    # TODO: subcats
    if (category_name == None):
        category_name = 'all'

    category = Category.query.filter_by(url_name = category_name).one()


    # TODO: add pagination
    if (category_name == 'all'):
        users = User.query.filter_by(doer=True, deleted=False).order_by(User.rating.desc()).all()
    else:
        users = category.doers_query.filter_by(doer=True, deleted=False).order_by(User.rating.desc()).all()

    return render_template('user/list.html', **{
        'users': users,
        'selected_category': category,
        'categories': Category.query.all()
    })

def get_categories_hierarchy(user):
    all_cats_hierarchy = {}
    for category in Category.query.all():
        if category.isSuperCategory: continue
        if not category.isSubCategory and category.url_name not in all_cats_hierarchy:
            all_cats_hierarchy[category.url_name] = {
                'data': category,
                'children': []
            }
        elif category.isSubCategory:
            if category.parent.url_name not in all_cats_hierarchy:
                all_cats_hierarchy[category.parent.url_name] = {
                    'data': category.parent,
                    'children': []
                } 
            all_cats_hierarchy[category.parent.url_name]['children'].append({
                'id': category.id,
                'name': category.name,
                'url_name': category.url_name,
                'done_by_this_user': category in user.task_categories
            })
    return all_cats_hierarchy

@frontend.route('users/<int:id>/', methods=['GET'])
def user_view(id):
    user = User.query.get(id)
    if user == None:
        abort(404)

    if (user.deleted):
        return render_template('user/deleted.html')
    # Forms a dictionary structured like
    # {'category_name1': {'data': category1, 'children': [subcategory1, subcategory2, ...]}, 'category_name2': ... }
    if user.doer:
        cat_hierarchy = {}
        for category in user.task_categories:
            if category.isSuperCategory: continue
            if not category.isSubCategory and category.url_name not in cat_hierarchy:
                cat_hierarchy[category.url_name] = {
                    'data': category,
                    'children': []
                }
            else:
                if category.parent.url_name not in cat_hierarchy:
                    cat_hierarchy[category.parent.url_name] = {
                        'data': category.parent,
                        'children': []
                    } 
                cat_hierarchy[category.parent.url_name]['children'].append(category)

        all_cats_hierarchy = get_categories_hierarchy(current_user)


                
    from sqlalchemy.sql import func
    from project.modules.user_rating import UserRating
    from project.database import db
    #print( db.session.query(func.avg(UserRating.value).label('average')).filter(UserRating.owner_id==user.id).one()[0] )

    return render_template('user/profile.html', **{
        'user': user,
        'task_categories' : cat_hierarchy if user.doer else None,
        'all_categories_hierarchy' : all_cats_hierarchy if user.doer else None,
        'received_comments': user.received_comments.order_by(UserComment.created_at.desc()),
        'portfolio_items': Upload.query.filter_by(author=user, role='portfolio').all()
    })

@frontend.route('reg/', methods=('GET', 'POST'))
def reg():
    form = RegistrationForm()

    # TODO: Exception handling
    if form.validate_on_submit():
        try:
            user, password = create_user(
                fullname = form.fullname.data,
                email = form.email.data,
                phone = normalize_mobile(form.phone.data),
                city = form.city.data
            )
        except EmailExistsException:
            form.email.errors.append('Вы ввели e-mail, который уже используется. Пожалуйста, не регистрируйте более одного аккаунта на один адрес e-mail.')
        else:
            login_user(form.email.data, password, remember=True)
            return redirect(get_redirect_url(form))

    #print('ERRORS: {}'.format(form.errors))
    return render_template('user/reg.html',
        reg_form = form
    )

@frontend.route('login/', methods=['GET', 'POST'])
def login():
    #print('SECRET_KEY: {}'.format(app.config['SECRET_KEY']))
    next = get_redirect_target()
    form = LoginForm()
    # TODO: Exception handling
    if form.validate_on_submit():
        # TODO: Login
        email = form.email.data
        password = form.password.data
        remember_flag = form.remember_me.data
        
        try:
            #print('LOGGING IN: ', login_user(email, password, remember=remember_flag))
            login_user(email, password, remember=remember_flag)
            return redirect(url_for('frontend.index'))
        except InvalidEmailException:
            form.email.errors.append('Такой e-mail не зарегистрирован!')
        except InvalidPasswordException:
            form.password.errors.append('Неверный пароль!')

    return render_template('user/login.html',
        login_form = form,
        next = next
    )

@frontend.route('logout/', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('frontend.index'))


def get_mobile_confirmation_cooldown(user_id):
    last_confirmation = MobileConfirmation.query.filter_by(user_id=user_id).order_by(MobileConfirmation.created_at.desc()).first()
    if last_confirmation:
        cooldown = max((last_confirmation.created_at + dt.timedelta(seconds=20) - dt.datetime.utcnow()).total_seconds(), 0)
    else:
        cooldown = 0
    return cooldown


@frontend.route('send_mobile_confirmation_sms/', methods=['POST'])
@rights_required('user')
def send_mobile_confirmation_sms():
    if get_mobile_confirmation_cooldown(current_user.id) <= 0:
        code = ''.join(random.sample('123456789' * 6, 6)) # TODO: вынести в отдельный хелпер
        confirmation = MobileConfirmation(code=code, user_id=current_user.id)
        try:
            db.session.add(confirmation)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        sms.send_sms(
            phone=current_user.phone,
            text=code,
            test=False
        )

    return redirect(url_for('frontend.confirm_mobile'))

@frontend.route('confirm_mobile/', methods=['GET', 'POST'])
@rights_required('user')
def confirm_mobile():
    if current_user.phone_confirmed:
        return render_template('user/mobile_confirmation_success.html')

    cooldown = get_mobile_confirmation_cooldown(current_user.id)
    form = MobileConfirmationForm()

    if form.validate_on_submit():
        code = form.code.data.strip()
        confirmation = MobileConfirmation.query.filter_by(code=code, user_id=current_user.id).first()
        if not confirmation:
            form.code.errors.append('Неправильный код подтверждения.')
        else:
            user = confirmation.user
            try:
                user.phone_confirmed = True
                MobileConfirmation.query.filter_by(user_id=user.id).delete()
                db.session.commit()
            except:
                db.session.rollback()
                raise
            try:
                return render_template('user/mobile_confirmation_success.html')
            except:
                return redirect(url_for('frontend.index'))

    return render_template('user/mobile_confirmation.html', **{
        'confirmationForm': form,
        'cooldown': cooldown
    })

@frontend.route('request_doer_rights/', methods=['GET', 'POST'])
@rights_required('user')
def request_doer_rights():
    # Если пользователь уже проверенный, отправляем в профиль
    if current_user.rights == 'trusted':
        return redirect(url_for('frontend.user_view', id=current_user.id))

    form = DoerApplicationForm()

    if form.validate_on_submit():
        if form.truthy_info.data != True or form.handling_okay.data != True:
            form.truthy_info.errors.append('Вы должны согласиться с условиями.')
        elif len(current_user.task_categories) == 0:
            form.truthy_info.errors.append('Вы должны выбрать хотя бы одну категорию заданий, которые вы собираетесь выполнять.')
        else:
            if current_user.phone_confirmed:
                if DoerApplication.query.filter_by(user_id=current_user.id).count() == 0:

                    try:
                        passport = upload_file(
                            request.files[form.passport_scan.name],
                            role='passport',
                            author_id=current_user.id
                        )
                    except FileTypeNotAllowed:
                        form.passport_scan.errors.append('Вы пытаетесь загрузить недопустимый тип файла.')
                    else:
                        application = DoerApplication(
                            user_id=current_user.id,
                            passport_scan_id=passport.id
                        )
                        try:
                            db.session.add(application)
                            db.session.commit()
                        except:
                            db.session.rollback()
    application_exists = DoerApplication.query.filter_by(user_id=current_user.id).count() > 0
    return render_template('user/request_doer_rights.html', **{
        'application_exists': application_exists,
        'applicationForm': form,
        'all_categories_hierarchy': get_categories_hierarchy(current_user)
    })

@frontend.route('change_avatar/', methods=['GET', 'POST'])
@rights_required('user')
def change_avatar():
    form = ChangeAvatarForm()

    if form.validate_on_submit():
        try:
            avatar = upload_file(
                request.files[form.avatar.name],
                role='avatar',
                author_id=current_user.id
            )
        except FileTypeNotAllowed:
            form.avatar.errors.append('Вы пытаетесь загрузить недопустимый тип файла.')
        else:
            try:
                current_user.avatar_id = avatar.id
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                form.avatar.errors.append(str(e))
            else:
                return redirect(url_for('frontend.user_view', id=current_user.id))
            
    return render_template('user/change_avatar.html', **{
        'avatarForm': form
    })

@frontend.route('remove_avatar/', methods=['GET', 'POST'])
@rights_required('user')
def remove_avatar():
    if current_user.avatar:
        try:
            avatar = current_user.avatar
            current_user.avatar_id = None
            # TODO: Удалять только если точно ничего больше сюда не ссылается
            #db.session.delete(avatar)
            db.session.commit()
        except:
            db.session.rollback()
            raise
    return redirect(url_for('frontend.user_view', id=current_user.id))

@frontend.route('social_login/', methods=['GET', 'POST'])
def social_login():
    token = request.form.get('token', None)
    host = config['flask']['SERVER_NAME']

    if not token:
        raise Exception('Invalid token: ' + str(token))
    if not host:
        raise Exception('Invalid host: ' + str(host))

    r = requests.get('http://ulogin.ru/token.php?token=' + str(token) + '&host=' + str(host))
    user_data = json.reads(r)

    if 'error' in user_data:
        raise Exception(str(user_data))

    network = user_data.get('network', None)
    identity = user_data.get('identity', None)

    data = UloginData.query.filter_by(network=network, identity=identity).first()
    if data:
        login_user_object(data.user)
        return redirect(url_for('frontend.index'))

    full_name = user_data.get('first_name', '') + ' ' + user_data.get('last_name', '')
    if len(full_name.strip()) == 0:
        return 'Invalid result: full name is empty'

    email = user_data['email']
    city = user_data['city']
    phone = user_data['phone']

    if current_user.is_authenticated():
        try:
            db.session.add( UloginData(user_id=current_user.id, network=network, identity=identity) )
            db.session.commit()
        except:
            db.session.rollback()
    else:
        user, _ = create_user(email=email, fullname=full_name, city=city, phone=normalize_mobile(phone))
        login_user_object(user)

    return redirect(url_for('frontend.index'))
    
@frontend.route('restore_password/', methods=['GET', 'POST'])
def restore_password():
    form = RestorePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if not user:
            form.email.errors.append("Пользователь с адресом электронной почты " + str(form.email.data) + " не найден.")
        else:
            date = str(dt.datetime.now().date())
            old_password = user.password
            restoration_hash = hashlib.sha1( (user.password + date).encode('utf-8') ).hexdigest()
            
            mail.send_mail(
                subject="Восстановление пароля movesol.ru",
                body=render_template('letters/restore_password.html', **{
                    'user': user,
                    'hash': restoration_hash
                }),
                recipients=[user.email],
                sender=(config['website']['mail_name'], config['website']['mail_address'])
            )
            return render_template('user/password_restoration_sent.html', **{ 'email': user.email })
    return render_template('user/restore_password.html', **{
        'form': form
    })

@frontend.route('do_restore_password/<id>/<hash>/')
def do_restore_password(id, hash):
    user = User.query.filter_by(id=id).first()
    if not user:
        abort(404)
       
    now = dt.datetime.now()
    yesterday = now - dt.timedelta(days=1)
    tomorrow = now + dt.timedelta(days=1)
    
    valid_hashes = [
        hashlib.sha1( (user.password + str(now.date())).encode('utf-8') ).hexdigest(),
        hashlib.sha1( (user.password + str(yesterday.date())).encode('utf-8') ).hexdigest(),
        hashlib.sha1( (user.password + str(tomorrow.date())).encode('utf-8') ).hexdigest()
    ]
    
    if hash in valid_hashes:
        pwd = gen_password(config['accounts']['generated_password_length'])
        set_user_password(user, pwd)
        
        mail.send_mail(
            subject="Ваш новый пароль movesol.ru",
            body=render_template('letters/your_new_password.html', **{
                'user': user,
                'password': pwd
            }),
            recipients=[user.email],
            sender=(config['website']['mail_name'], config['website']['mail_address'])
        )
        return render_template('user/password_restored.html', **{ 'user': user, 'password': pwd })
    
    abort(404)

@frontend.route('add_portfolio_item/', methods=['GET', 'POST'])
@rights_required('user')
def add_portfolio_item():
    form = AddPortfolioItemForm()

    if form.validate_on_submit():
        try:
            photo = upload_file(
                request.files[form.photo.name],
                role='portfolio',
                author_id=current_user.id,
                description=form.description.data
            )
        except FileTypeNotAllowed:
            form.photo.errors.append('Вы пытаетесь загрузить недопустимый тип файла.')
        else:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                form.photo.errors.append(str(e))
            else:
                return redirect(url_for('frontend.user_view', id=current_user.id))
            
    return render_template('user/add_portfolio_item.html', **{
        'form': form
    })