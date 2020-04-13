from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectMultipleField, HiddenField, RadioField
from wtforms.validators import DataRequired

class SocketAssignmentForm(FlaskForm):
    remote = HiddenField('Remote')
    socket = HiddenField('Socket')
    name = StringField('Name')
    category = StringField('Kategorie')
    timer_switch = BooleanField('Zeitschaltuhr')
    start = StringField('Von')
    end = StringField('Bis')
    monday = BooleanField('Mo.')
    tuesday = BooleanField('Di.')
    wednesday = BooleanField('Mi.')
    thursday = BooleanField('Do.')
    friday = BooleanField('Fr.')
    saturday = BooleanField('Sa.')
    sunday = BooleanField('So.')

class AudioOutputForm(FlaskForm):
    audio_output = RadioField(choices=[('hdmi', 'HDMI'), ('box', 'Boxen'), ('auto', 'Auto')])
