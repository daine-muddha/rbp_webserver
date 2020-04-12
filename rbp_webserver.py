from flask import Flask
from flask import render_template, redirect
from config import Config
from forms import SocketAssignmentForm

import json
import os

app = Flask(__name__)
app.config.from_object(Config)

class Data(object):
	url = r'C:\Users\danie\Development\rbp_webserver\rbp_webserver\data.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/funky')
def funky():
	with open(Data.url) as file:
		data = json.load(file)
		categories = dict()
		for funk in data["funksteckdosen"]:
			temp_dict = funk["settings"].copy()
			temp_dict["remote"] = funk["remote"]
			temp_dict["socket"] = funk["socket"]
			category = categories.get(funk["settings"]["category"], None)
			if category is None:
				categories[funk["settings"]["category"]] = [temp_dict]
			else:
				category.append(temp_dict)
				categories[funk["settings"]["category"]] = category
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
        return redirect(url_for('funky'))
    except:
        return render_template('ooops.html')

@app.route('/settings')
def settings():
	with open(Data.url) as file:
		data = json.load(file)
		forms = list()
		for funk in data["funksteckdosen"]:
			form = SocketAssignmentForm(**funk['settings'], remote=funk["remote"], socket=funk["socket"])
			forms.append(form)

	return render_template('settings.html', forms=forms)

@app.route('/music')
def music():
	return render_template('music.html')

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)