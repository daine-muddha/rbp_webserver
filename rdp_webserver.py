from flask import Flask
from flask import render_template
import os
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/funky')
def funky():
    return render_template('funky.html')

@app.route('/funky/<string:remote>_<int:socket>_<string:turn>')
def turn_socket_on_off(remote, socket, turn):
    try: 
        os.system('rfsniffer play {}.{}{}'.format(remote, socket, turn))
        return render_template('funky.html')
    except:
        return render_template('ooops.html')

if __name__=='__main__':
    app.run(host='0.0.0.0', port=80, debug=True)