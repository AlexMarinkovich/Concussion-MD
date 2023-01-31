from flask import Flask, request, jsonify
from flask_cors import CORS
from without_plots import get_concussion_level
import pygsheets as pygsheets

app = Flask(__name__)
CORS(app)

@app.route("/")
def default_message():
    return "Hello World"

@app.route("/processvideo", methods=['GET','POST'])
def process_video():
    base64data = request.get_json()
    get_concussion_level(base64data['videodata'])

@app.route("/getresult")
def get_result():
    gc = pygsheets.authorize(service_file='/home/alexMarinkovich/mysite/creds.json')
    sh = gc.open('QHacks')
    wks = sh.sheet1
    return jsonify(str(wks.get_value("A1")))

if __name__ == "__main__":
    app.run()