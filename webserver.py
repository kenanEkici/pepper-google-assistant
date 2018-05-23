from flask import Flask, request, send_file, render_template
from gtts import gTTS
import configparser
import requests
import base64
from naoqi import ALProxy
from flask_socketio import SocketIO

my_server = Flask(__name__)
socketio = SocketIO(my_server)
uri = None
pepper = None
host = None
port = None

@my_server.route("/", methods=['GET'])
def root():
    return render_template('index.html')


@my_server.route("/texttospeech", methods=['GET'])
def tts():
    return render_template('tts.html')


@my_server.route("/tts", methods=['POST'])
def synthesize():
    req = request.json.get('input')
    tts = gTTS(text=req, lang='en')
    tts.save("syn.mp3")
    return "success"


@my_server.route("/tts", methods=['GET'])
def stream():
    return send_file('syn.mp3', cache_timeout=0)


@my_server.route("/google", methods=['GET'])
def streamwav():
    return send_file('syn.wav', cache_timeout=0)


@my_server.route("/google", methods=['POST'])
def gcloud():
    headers = {
        'Content-Type': 'application/json'
    }
    resp = requests.post("https://cxl-services.appspot.com/proxy?url=https%3A%2F%2Ftexttospeech.googleapis.com%2Fv1beta1%2Ftext%3Asynth$", headers=headers, json=request.json())
    r = resp.json().get('audioContent')
    with open("syn.mp3", 'w') as file:
        file.write(base64.decodestring(r))


@my_server.route("/pepper", methods=['POST'])
def peppertts():
    req = request.json.get('input')
    tts = ALProxy("ALTextToSpeech", pepper, 9559)
    tts.say(req)


@my_server.route("/pepper", methods=['GET'])
def play():
    audio = ALProxy("ALAudioPlayer", pepper, 9559)
    audio.playWebStream(uri, 1, 0)


def handle_message(msg_type, msg):
    socketio.emit(msg_type, msg)


def startserver():
    global uri, pepper, host, port
    config = configparser.ConfigParser()
    config.read('config.ini')

    host = config['IP']['Host']
    port = config['IP']['Port']

    uri = "http://" + str(host) + ":" + str(port) + "/google"
    pepper = str(config['IP']['Robot'])

    print("API is running")
    socketio.run(my_server, host=host, port=int(port))
