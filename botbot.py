from libs.flask import Flask
from libs import vk

app = Flask(__name__)
@app.route('/', methods=['POST'])
def processing():
	return 'Hello'