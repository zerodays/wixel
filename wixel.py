import board
import neopixel
from flask import Flask, jsonify, request

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
