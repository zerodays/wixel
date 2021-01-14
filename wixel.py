import threading
import time

import board
import neopixel
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

# Constants
PORT = 6969  # Port of HTTP server
NUMBER_OF_LED = 100  # Number of LEDs in the strip
DATA_PIN = board.D18  # Data pin on raspberry. Do not forget to uncomment it.
API_PREFIX = '/api/v1'  # prefix for api urls

app = Flask(__name__)

pixels = neopixel.NeoPixel(DATA_PIN, NUMBER_OF_LED)


@app.route(API_PREFIX + '/wix_enabled', methods=['GET'])
def is_wix_enabled():
    return jsonify(True)


@app.route(API_PREFIX + '/strip', methods=['GET'])
def get_strip():
    state = [(0, 0, 0)] * NUMBER_OF_LED
    for i in range(NUMBER_OF_LED):
        state[i] = pixels[i]

    return jsonify(state)


@app.route(API_PREFIX + '/strip', methods=['POST'])
def set_strip():
    req = request.get_json()
    length = min(len(req), len(pixels))
    for i in range(length):
        pixels[i] = req[i]

    return ''


@app.route(API_PREFIX + '/fade', methods=['POST'])
def fade():
    req = request.get_json()
    seconds = req['seconds']
    end_state = req['led'][:min(len(req['led']), len(pixels))]

    t = threading.Thread(target=fade_to, args=(seconds, end_state,))
    t.start()

    return ''


def fade_to(seconds, end_state):
    start_state = [(0, 0, 0)] * NUMBER_OF_LED
    for i in range(NUMBER_OF_LED):
        start_state[i] = pixels[i]

    start = datetime.now()
    end = start + timedelta(seconds=seconds)
    dt = 1 / 60

    while datetime.now() < end:
        now = datetime.now()
        delta = (now - start).total_seconds()
        progress = delta / seconds

        for i in range(NUMBER_OF_LED):
            r = start_state[i][0] * (1 - progress) + end_state[i][0] * progress
            g = start_state[i][1] * (1 - progress) + end_state[i][1] * progress
            b = start_state[i][2] * (1 - progress) + end_state[i][2] * progress
            pixels[i] = (int(r), int(g), int(b))

        delta = (datetime.now() - now).total_seconds()
        diff = dt - delta
        if diff > 0:
            time.sleep(diff / 1000)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
