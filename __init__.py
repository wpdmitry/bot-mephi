# coding: utf-8

from .settings import *
from flask import Flask, request, json
from .message_processing import new_message
from .group_activites import new_user, leave_user


app = Flask(__name__)


@app.route('/', methods=['POST'])
def get_callback():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    elif data['type'] == 'confirmation':
        return confirmation_token
    elif data['type'] == 'message_new':
        new_message(user_id=data['object']['user_id'],
                    message=data['object']['body'])
    elif data['type'] == 'group_join':
        new_user(data['object']['user_id'])
    elif data['type'] == 'group_leave':
        leave_user(data['object']['user_id'])
    return 'ok'


if __name__ == "__main__":
    app.run()