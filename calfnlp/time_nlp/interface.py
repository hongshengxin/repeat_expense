from flask import Flask, request
from TimeNormalizer import TimeNormalizer

app = Flask(__name__)

tn = TimeNormalizer()


@app.route('/time-recognition/parse', methods=['POST', 'GET'])
def time_recognite():
    re = None

    if request.method == 'GET':
        sentence = request.args.get('sentence')
        try:
            timebase = request.args.get('timebase')
            res = tn.parse(target=sentence, timeBase=timebase)
        except:
            res = tn.parse(target=sentence)
    else:
        sentence = request.form.get('sentence')
        try:
            timebase = request.form.get('timebase')
            res = tn.parse(target=sentence, timeBase=timebase)
        except:
            res = tn.parse(target=sentence)
    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
