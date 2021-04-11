import requests
from flask import Flask, request
import logging
import json
from flask_ngrok import run_with_ngrok


app = Flask(__name__)
run_with_ngrok(app)
logging.basicConfig(level=logging.INFO)


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    res['response']['buttons'] = [
                {
                    'title': 'Помощь',
                    'hide': True
                }
            ]
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я перевожу слова. Напишите: "Переведите (переведи) слово: *слово*", \
            - и я перевду введённое Вами слово.'
        return
    text = req['request']['original_utterance']
    t = text.split()
    if text.lower() == 'помощь':
        res['response']['text'] = 'Я перевожу слова. Напишите: "Переведите (переведи) слово: *слово*", \
            - и я перевду введённое Вами слово.'
    elif t[0].lower() in ['переведите', 'переведи'] and t[1].lower() in ['слово:', 'слово'] and len(t) == 3:
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': t[2],
            'langpair' : 'ru|en'
        }
        try:
            response = requests.get(url, params)
            data = response.json()
            res['response']['text'] = data['responseData']['translatedText']
        except Exception:
            res['response']['text'] = 'Не могу перевести. Попробуйте ещё раз.'
    else:
        res['response']['text'] = 'Я вас не понимаю. Напишите: "Переведите (переведи) слово: *слово*", \
            - и я перевду введённое Вами слово.'


if __name__ == '__main__':
    app.run()