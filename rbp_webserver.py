from flask import Flask
from flask import render_template, redirect, request, url_for
from config import Config
from forms import SocketAssignmentForm, AudioOutputForm
from werkzeug.datastructures import MultiDict

import json
import os
import urllib.parse

app = Flask(__name__)
app.config.from_object(Config)

class Data(object):
	url = '/home/pi/rbp_webserver/rbp_webserver/data.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/funky')
def funky():
	with open(Data.url) as file:
		data = json.load(file)
		categories = dict()
		#create dictionary where the keys are the different categories and the value is a list of the dicts containing a socket of this category
		for funk in data["funksteckdosen"]: 
			category = categories.get(funk["category"], None)
			if category is None:
				categories[funk["category"]] = [funk]
			else:
				category.append(funk)
				categories[funk["category"]] = category
		#convert dictionary to a list where each entry is a dictionary with one key/val pair being the name of this category 
		#and the other key/val pair being the list of dictionaries for this category (for template)
		cat_list = list()
		for key, val in categories.items():
			temp_dict = dict()
			temp_dict["name"] = key
			temp_dict["sockets"] = val
			cat_list.append(temp_dict)

	return render_template('funky.html', categories=cat_list)

@app.route('/funky/<string:remote>_<int:socket>_<string:turn>')
def turn_socket_on_off(remote, socket, turn):
    try: 
        os.system('rfsniffer play {}.{}{}'.format(remote, socket, turn))
        return redirect(url_for('/funky'))
    except:
        return render_template('ooops.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
	if request.method == 'GET':
		with open(Data.url) as file:
			data = json.load(file)
			forms = list()
			for funk in data["funksteckdosen"]:
				form = SocketAssignmentForm(MultiDict(funk))
				forms.append(form)
		return render_template('settings.html', forms=forms)
	elif request.method == 'POST':
		form_data = request.form['form_data']
		form_data = form_data.replace('=y&', '=true&')
		form_data = form_data.split('&formbreak&')
		form_data = form_data[:-1]
		json_list = list()
		for form in form_data:
			form_dict = urllib.parse.parse_qs(form)
			form_dict = {key:val[0] for key,val in form_dict.items()}
			form_obj = SocketAssignmentForm(MultiDict(form_dict))
			form_obj_data = form_obj.data
			form_obj_data.pop('csrf_token', None)
			json_list.append(form_obj_data)
		with open(Data.url, 'r') as file:
			data = json.load(file)
		data["funksteckdosen"] = json_list
		with open(Data.url, 'w') as file:
			json.dump(data, file, indent=4)

		return redirect(url_for('index'))

	

@app.route('/music', methods=['GET', 'POST'])
def music():
	if request.method == 'GET':
		volume=20
		form = AudioOutputForm(audio_output='box')
		return render_template('music.html', volume=volume, form=form)
	elif request.method == 'POST':
		volume = request.form.get('volume', None)
		if volume is not None:
			print(volume)
		audio_output = request.form.get('audio_output', None)
		if audio_output is not None:
			print(audio_output)

		return 'OK'


if __name__=='__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)