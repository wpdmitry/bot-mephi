import vk
from .settings import *


inessa_id = 84479928
session = vk.Session(access_token=token)
api = vk.API(session)


def new_user(user_id):
    user_info = api.users.get(user_ids=user_id)[0]

    name = user_info['first_name'] + ' ' + user_info['last_name']
    message = '&#10133; *id{user_id}({name}) в сообществе.\n' \
              '&#128140; Инессочка, я очень тебя люблю.'.format(user_id=user_id, name=name)

    api.messages.send(user_id=inessa_id, message=message)


def leave_user(user_id):
    user_info = api.users.get(user_ids=user_id)[0]

    name = user_info['first_name'] + ' ' + user_info['last_name']
    message = '&#10134; *id{user_id}({name}) в сообществе.\n' \
              '&#128140; Инессочка, я очень тебя люблю.'.format(user_id=user_id, name=name)

    api.messages.send(user_id=inessa_id, message=message)