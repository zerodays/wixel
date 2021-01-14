import threading
import time
from datetime import datetime, timedelta

import board
import neopixel
from flask import Flask, jsonify, request

# Constants
PORT = 6969  # Port of HTTP server
NUMBER_OF_LED = 100  # Number of LEDs in the strip
DATA_PIN = board.D18  # Data pin on raspberry. Do not forget to uncomment it.
SWITCHED_GB = True  # Are green and blue switched.
API_PREFIX = '/api/v1'  # prefix for api urls

app = Flask(__name__)

pixels = neopixel.NeoPixel(DATA_PIN, NUMBER_OF_LED, auto_write=False)

fading = False
after_fade = None


@app.route(API_PREFIX + '/wix_enabled', methods=['GET'])
def is_wix_enabled():
    return jsonify(True)


@app.route(API_PREFIX + '/strip', methods=['GET'])
def get_strip():
    state = [(0, 0, 0)] * NUMBER_OF_LED
    for i in range(NUMBER_OF_LED):
        if SWITCHED_GB:
            state[i] = (pixels[i][0], pixels[i][2], pixels[i][1])
        else:
            state[i] = pixels[i]

    return jsonify(state)


@app.route(API_PREFIX + '/strip', methods=['POST'])
def set_strip():
    global after_fade

    def set_led(state):
        global after_fade

        for i in range(NUMBER_OF_LED):
            if SWITCHED_GB:
                pixels[i] = (state[i][0], state[i][2], state[i][1])
            else:
                pixels[i] = state[i]

        pixels.show()

    state = request.get_json()
    if fading:
        after_fade = lambda: set_led(state)
    else:
        set_led(state)

    return ''


@app.route(API_PREFIX + '/fade', methods=['POST'])
def fade():
    global fading, after_fade
    if fading:
        return ''

    def exec_fade(seconds, end_state):
        global fading
        fading = True

        t = threading.Thread(target=fade_to, args=(seconds, end_state,))
        t.start()

    req = request.get_json()
    seconds = req['seconds']
    end_state = req['led']
    if SWITCHED_GB:
        for i in range(len(end_state)):
            end_state[i][1], end_state[i][2] = end_state[i][2], end_state[i][1]

    if fading:
        after_fade = lambda: exec_fade(seconds, end_state)
    else:
        exec_fade(seconds, end_state)

    return ''


def fade_to(seconds, end_state):
    global fading, after_fade

    start_state = [(0, 0, 0)] * NUMBER_OF_LED
    for i in range(NUMBER_OF_LED):
        start_state[i] = pixels[i]

    start = datetime.now()
    end = start + timedelta(seconds=seconds)
    dt = 1 / 100

    while datetime.now() < end:
        now = datetime.now()
        delta = (now - start).total_seconds()
        progress = delta / seconds

        for i in range(NUMBER_OF_LED):
            r = start_state[i][0] * (1 - progress) + end_state[i][0] * progress
            g = start_state[i][1] * (1 - progress) + end_state[i][1] * progress
            b = start_state[i][2] * (1 - progress) + end_state[i][2] * progress
            pixels[i] = (int(r), int(g), int(b))

        pixels.show()

        delta = (datetime.now() - now).total_seconds()
        diff = dt - delta
        if diff > 0:
            time.sleep(diff)

    for i in range(NUMBER_OF_LED):
        r = end_state[i][0]
        g = end_state[i][1]
        b = end_state[i][2]
        pixels[i] = (int(r), int(g), int(b))
    pixels.show()

    fading = False

    if after_fade is not None:
        after_fade()
        after_fade = None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
