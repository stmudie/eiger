from flask import Flask, render_template, send_file

from eigerclient import DEigerClient
from eigertest2 import EigerTest

app = Flask(__name__)

@app.route('/')
def top():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
