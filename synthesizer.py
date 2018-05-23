from naoqi import ALProxy
import requests
import json
import configparser
import base64


def play(uri, robot):
    audio = ALProxy("ALAudioPlayer", robot, 9559)
    audio.playWebStream(uri, 1, 0)


def gtts(text):
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        'input': text
    }
    requests.post(uri, headers=headers, data=json.dumps(payload))


def gcloud(text):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "input":
            {
                "text":text
            },
        "voice":
            {
                "languageCode":"en-US","name":"en-US-Wavenet-D"
            },
        "audioConfig":
            {
                "audioEncoding":"LINEAR16",
                "pitch":"0.00",
                "speakingRate":"1.00"
            }
    }
    resp = requests.post("https://cxl-services.appspot.com/proxy?url=https%3A%2F%2Ftexttospeech.googleapis.com%2Fv1beta1%2Ftext%3Asynthesize", headers=headers, data=json.dumps(payload))
    r = resp.json().get('audioContent')
    with open("syn.mp3", 'w') as file:
        file.write(base64.decodestring(r))


def pepper(text):
    tts = ALProxy("ALTextToSpeech", robot, 9559)
    tts.say(text)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    uri = "http://" + str(config['IP']['Host']) + ":" + str(config['IP']['Port']) + "/tts"
    robot = str(config['IP']['Robot'])

    choice = raw_input("Choose Text-to-Speech system: 1 = Pepper, 2 = GTTS, 3 = Google Cloud TTS\n")
    while True:
        inp = raw_input("Please input the text to be synthesized. Input 'Stop' to quit or 'Choice' to change TTS mode\n")
        if inp == "Choice": 
             choice = raw_input("Choose Text-to-Speech system: 1 = Pepper, 2 = GTTS, 3 = Google Cloud TTS\n")
             inp = raw_input("Please input the text to be synthesized. Input 'Stop' to quit or 'Choice' to change TTS mode\n")
        if inp != "Stop":
            if choice == "1":
                pepper(inp)
            if choice == "2":
                gtts(inp)
                print("Synthesized text")
                play(uri, robot)
                print("Played speech")
            if choice == "3":
                gcloud(inp)
                print("Synthesized text")
                play(uri, robot)
                print("Played speech")
        else:
            pepper("I was only learning to love")
            break
