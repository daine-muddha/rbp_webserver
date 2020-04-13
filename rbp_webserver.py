from flask import Flask
from flask import render_template, redirect, request, url_for
from config import Config
from data import Data
from forms import SocketAssignmentForm, AudioOutputForm
from py_crontab import update_timer_switches
from time import sleep
from werkzeug.datastructures import MultiDict

import json
import os
import subprocess
import urllib.parse

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/funky', methods=['GET', 'POST'])
def funky():
    if request.method == 'GET':
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

    elif request.method == 'POST':
        btn_id = request.form['btn_id']
        btn_id = btn_id.split('+')
        try:
            os.system('rfsniffer play {}.{}{}'.format(btn_id[0].lower(), btn_id[1], btn_id[2]))
            return 'OK'
        except:
            return redirect(url_for('ooops'))
        

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
        update_timer_switches()
        return redirect(url_for('index'))

    

@app.route('/music', methods=['GET', 'POST'])
def music():
    min_volume=0
    max_volume=10639
    if request.method == 'GET':
        #get volume
        process = subprocess.Popen(['amixer', '-M', '-sget', 'PCM'], stdout=subprocess.PIPE)
        stdout = process.communicate()[0].decode('utf-8')
        output_split = stdout.split(':')
        volume_str = output_split[-1]
        search_str = '['
        volume_start_ind=volume_str.find(search_str)+len(search_str)
        volume_end_ind = volume_str.find('%')
        volume = int(volume_str[volume_start_ind:volume_end_ind])
        #get audio output
        process = subprocess.Popen(['amixer', 'cget', 'numid=3'], stdout=subprocess.PIPE)
        stdout = process.communicate()[0].decode('utf-8')
        audio_out_val_str = stdout.split(':')[-1]
        search_str = 'values='
        audio_out_val_ind=audio_out_val_str.find(search_str)+len(search_str)
        audio_out_val = int(audio_out_val_str[audio_out_val_ind])
        audio_output=''
        if audio_out_val==0:
            audio_output='auto'
        elif audio_out_val==1:
            audio_output='box'
        elif audio_out_val==2:
            audio_output='hdmi'
        form = AudioOutputForm(audio_output=audio_output)
        return render_template('music.html', volume=volume, form=form)
    elif request.method == 'POST':
        volume = request.form.get('volume', None)
        if volume is not None:
            try:
                volume= int(volume)
                os.system('amixer -q -M sset PCM {}%'.format(volume))
                return 'OK'
            except:
                return 'Not OK'

        audio_output = request.form.get('audio_output', None)
        if audio_output is not None:
            if audio_output=='auto':
                audio_out_val=0
            elif audio_output=='box':
                audio_out_val=1
            elif audio_output=='hdmi':
                audio_out_val=2
            try:
                os.system('amixer cset numid=3 {}'.format(audio_out_val))
                return 'OK'
            except:
                return 'Not OK'
        

@app.route('/ooops')
def ooops():
    return render_template('ooops.html')


if __name__=='__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
