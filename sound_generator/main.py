import json

from flask import Flask, request, jsonify
from sound_generator import get_prediction


app = Flask(__name__)


@app.route('/sound/', methods=['POST'])
def api():
    data = json.loads(request.data)
    prediction, success = get_prediction(data)
    return jsonify({'audio': prediction.tolist(), 'success': success})


if __name__ == '__main__':
    app.run()
