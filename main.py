from flask import Flask, request, send_file
import os
import openai
from elevenlabs import generate, play, set_api_key, save
import time
import keys

app = Flask(__name__)
openai.api_key = keys.OPENAI_KEY
set_api_key(keys.ELEVENLABS_KEY)
jason_messages = [
    {"role": "system", "content": "Your name is Bella, and you are a gentle and friendly conversationalist."}]


@app.route('/', methods=['GET'])
def home():
    return app.send_static_file('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    # 从POST请求中获取FormData对象
    audio = request.files.get('audio')
    audio.save('./static/audio.webm')
    text = audio_2_text()
    assistant_text = chat(text)
    text_2_speech(assistant_text)
    filename = "./static/Bella.mp3"
    return send_file(filename, mimetype="audio/mp3")


def audio_2_text():
    audio_file = open('./static/audio.webm', "rb")
    transcript = openai.Audio.translate("whisper-1", audio_file)['text']
    return transcript


def chat(user_content):
    userjson = {'role': 'user', 'content': user_content}
    jason_messages.append(userjson)
    while True:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=jason_messages
            )
            break
        except Exception as e:
            print(e)
            time.sleep(2)  # 等待 2 秒后重试

    assistant_content = completion.choices[0].message['content']
    assistantjson = {'role': 'assistant', 'content': assistant_content}
    jason_messages.append(assistantjson)
    retain_10_conversation()
    return assistant_content


def text_2_speech(text):
    audio = generate(
        text=text,
        voice="Bella",
        model='eleven_monolingual_v1'
    )
    save(audio, './static/Bella.mp3')


def retain_10_conversation():
    if len(jason_messages) >= 11:
        jason_messages.pop(1)
        jason_messages.pop(2)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=80)
