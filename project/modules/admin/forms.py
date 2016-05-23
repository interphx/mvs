from wtforms import FieldList, BooleanField, DecimalField, FloatField, TextField, TextAreaField, PasswordField, BooleanField, validators
from flask.ext.wtf import Form

class ForgivingFloatField(FloatField):
    def process_formdata(self, formdata):
        self.data = None
        if formdata:
            self.data = float(formdata[0].replace(',', '.').replace(' ', '').strip())

class ChangeSettingsForm(Form):
    slogan = TextField('Слоган', [
    	validators.Length(max=4096, message='Слоган сайта не может быть таким большим.')
    ])

    seo_keywords = TextField('Ключевые слова (тег keywords)')
    seo_description = TextField('Описание (тег description)')

    #commission = ForgivingFloatField('Комиссия', validators=[
    #	validators.NumberRange(min=0.0, max=1.0, message='Доля комиссии должна выражаться числом от 0 до 1.')
    #])

    commission_ranges = TextAreaField('Комиссия')

class LetterForm(Form):
    text = TextAreaField('Текст письма')