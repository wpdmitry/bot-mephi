# coding: utf-8

import vk, os, random
from .settings import *
from .database import logging_user
from .scheduling import answer_to_r
from .basic_functions import parse_message, waiting, get_schedule, report, logging_message
from .welcome import welcome


session = vk.Session(access_token=token)
api = vk.API(session)


class User:
    def __init__(self, user_id, message):
        self.id = user_id
        self.message = message.strip().upper()

    def get_name(self):
        user_info = api.users.get(user_ids=self.id)[0]
        self.first_name = user_info['first_name']
        self.last_name = user_info['last_name']


class Bot:
    def __init__(self, user):
        self.user = user

    def bot_say(self, text):
        api.messages.send(user_id=self.user.id, message=text)
        return

    def bot_say_welcome(self):
        self.bot_say(welcome(self.user.first_name))
        return

    @staticmethod
    def bot_say_schedule(bot, name_group, time_label):
        text_answer = ''
        for times in time_label:
            answr = answer_to_r(bot, name_group, times)
            if not answr:
                bot.bot_say('Что-то пошло не так')
                return None
            elif answr == 'Not found group':
                return 'Not found group'
            text_answer += answr
        return text_answer


def new_message(user_id, message):
    user = User(user_id=user_id, message=message)
    bot = Bot(user)

    logging_message(user)

    try:
        if os.path.exists(path_wait_user + str(user.id) + '.wait.txt'):
            wait = waiting(user, bot)
            if not wait: return

        label = logging_user(user)
        if label:
            bot.bot_say_welcome()
            return

        result = parse_message(user.message)
        if 'schedule' in result:
            get_schedule(user, bot, result)
            return

        elif 'hello' in result:
            bot.bot_say(random.choice(hello_words).capitalize())
            return

        elif 'thanks' in result:
            bot.bot_say(random.choice(answer_thank))
            return

        elif 'error' in result:
            raise NameError('Eeee biiich')

        else:
            bot.bot_say('Твоя просьба вне моих компетенций. Мой конек - расписание.')
            return

    except Exception as error_name:
        report(user, bot, error_name, api)
        return
