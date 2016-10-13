from wtforms import BooleanField, TextField, PasswordField, BooleanField, FileField, validators
from wtforms.fields.html5 import EmailField
from flask.ext.wtf import Form

from project.util import normalize_mobile

class RegistrationForm(Form):
    fullname = TextField('Полное имя', [validators.Length(min=1, max=100, message='Полное имя должно содержать не менее 1 и не более 100 букв.')])
    email = EmailField('E-mail', [validators.DataRequired(message='Пожалуйста, укажите коррекнтый e-mail.'), validators.Email(message='Пожалуйста, укажите корректный e-mail.')])
    phone = TextField('Телефон', [])
    city = TextField('Город', [validators.Length(min=1, max=100, message='Пожалуйста, укажите город.')])
    
    def validate_phone(form, field):
        # +7 и ещё 10 цифр
        PHONE_LENGTH = 12
        phone = field.data
        if not phone or len(normalize_mobile(phone)) != PHONE_LENGTH:
            raise validators.ValidationError('Номер телефона должен содержать ровно 10 цифр, не считая +7.')

class LoginForm(Form):
    email = TextField('E-mail', [validators.Length(min=4, max=100, message='E-mail не может быть короче 4 или длиннее 100 знаков.')])
    password = PasswordField('Пароль', [validators.Length(min=1, max=100, message='Длина пароля не может превышать 100 знаков. Необходимо ввести правильный пароль.')])
    remember_me = BooleanField('Запомнить меня', default=True)

class MobileConfirmationForm(Form):
    code = TextField('Код подтверждения')

class DoerApplicationForm(Form):
    truthy_info = BooleanField('Я подтверждаю, что информация на моей странице является достоверной')
    first_time = BooleanField('Я прохожу верификацию впервые')
    handling_okay = BooleanField('Я соглашаюсь с тем, что мои пересональные данные будут обработаны администрацией без передачи их третьим лицам')
    passport_scan = FileField('Скан паспорта', validators=[validators.InputRequired(message='Необходимо загрузить скан паспорта.')])

class ChangeAvatarForm(Form):
    avatar = FileField('Фото', validators=[validators.InputRequired(message='Необходимо приложить фото.')])

class AddPortfolioItemForm(Form):
    photo = FileField('Фотография', validators=[validators.InputRequired(message='Необходимо приложить фотографию.')])
    description = TextField('Описание (необязательно)')

class RestorePasswordForm(Form):
    email = TextField('E-mail')