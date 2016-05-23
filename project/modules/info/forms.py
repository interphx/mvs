from wtforms import BooleanField, TextField, PasswordField, BooleanField, validators
from flask.ext.wtf import Form

class InfoPageForm(Form):
    title = TextField('Заголовок', [validators.Length(min=1, max=500, message='Название должно содержать не менее 1 и не более 500 символов.')])
    text = TextField('Текст', [validators.Length(min=1, message='Текст не может бть пустым.')])