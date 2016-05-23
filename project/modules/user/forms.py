from wtforms import BooleanField, TextField, PasswordField, BooleanField, FileField, validators
from flask.ext.wtf import Form

class RegistrationForm(Form):
    fullname = TextField('Полное имя', [validators.Length(min=1, max=100, message='Полное имя должно содержать не менее 1 и не более 100 букв.')])
    email = TextField('E-mail', [validators.Length(min=4, max=100, message='E-mail не может быть короче 4 или длиннее 100 знаков.')])
    phone = TextField('Телефон', [validators.Length(min=4, max=100, message='Номер телефона должен содержать не менее 4 и не более 100 знаков.')])
    city = TextField('Город', [validators.Length(min=1, max=100, message='Пожалуйста, укажите город.')])

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