from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired

class SocketAssignmentForm(FlaskForm):
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

	def __init__(self, remote, socket, *args, **kwargs):
		super(SocketAssignmentForm, self).__init__(*args, **kwargs)
		self.remote = remote
		self.socket = socket
