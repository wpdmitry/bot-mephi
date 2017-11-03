import os, re, time, json, logging
from .help import help_request_user
from .settings import *


class open_to_flow():
    def __init__(self, filename, mode='r', lock_file=path_bot322 + 'lock.txt'):
        self.lock_file = lock_file
        while True:
            if os.path.exists(lock_file): continue
            else: break
        open(lock_file, 'w').close()
        self.f = open(filename, mode, encoding='utf8')

    def __enter__(self):
        return self.f

    def __exit__(self, *args):
        self.f.close()
        os.remove(self.lock_file)


def logging_message(user):
    import datetime
    with open_to_flow(filename=path_logging + 'logging_message.txt', mode='a',
                      lock_file=path_logging + 'lock.txt') as f:
        f.write(str(user.id) + '|' + user.message + '|' + datetime.datetime.today().strftime('%d.%m.%y %H:%M:%S') + '\n')
    return


def parse_message(text):
    norm_text = re.sub('[\.\?\!\,]', '', text)
    list_words = norm_text.split(' ')

    vector_answer = {}
    for word in list_words:
        if word == 'ОШИБКА':
            vector_answer['error'] = 1

        if word in schedule_words:
            vector_answer['schedule'] = 1

        if word in hello_words:
            vector_answer['hello'] = 1

        if word in thank_words:
            vector_answer['thanks'] = 1

        if word in time_words:
            try:
                vector_answer['time_label'].append(word)
            except KeyError:
                vector_answer['time_label'] = [word]

    return vector_answer


def search(text_users, dict_list):
    list_text_users = re.sub('[\.\?\!\,]', '', text_users).split(' ')
    answer = []

    for word in list_text_users:
        if word in dict_list:
            answer.append(word)

    return answer


def waiting(user, bot):
    from .database import get_user_command, save_command_for_user

    with open(path_wait_user + str(user.id) + '.wait.txt') as f:
        data = json.load(f)

    if (time.time() - data['timeout']) > 100:
        os.remove(path_wait_user + str(user.id) + '.wait.txt')
        bot.bot_say('В прошлый раз ты меня бросил! Не надо так.')
        return 'continue'
    else:
        if data['wait_label'] == 'time':
            result = search(user.message, time_words)
            if not result and data['attempt'] == 1:
                bot.bot_say(help_request_user('time'))
                with open(path_wait_user + str(user.id) + '.wait.txt', 'w') as f:
                    json.dump({'timeout': time.time(), 'wait_label': 'time', 'attempt': 2}, f)
                return
            elif not result and data['attempt'] == 2:
                bot.bot_say('Так бывает, что люди не понимают друг друга... рил ток синк эбаут ит')
                os.remove(path_wait_user + str(user.id) + '.wait.txt')
                return

            remember_group = get_user_command(user)
            if not remember_group:
                bot.bot_say('Уточни номер группы.')
            else:
                bot.bot_say('Уточни номер группы или выбери позицию из предложенных мной: \n{}'.format(remember_group))
            with open(path_wait_user + str(user.id) + '.wait.txt', 'w') as f:
                for k, time_label in enumerate(result):
                    if time_label in norm_date_day:
                       result[k] = norm_date_day[time_label]
                json.dump({'timeout': time.time(), 'wait_label': 'group', 'attempt': 1, 'time': result}, f)
            return

        elif data['wait_label'] == 'group':
            remember_group = get_user_command(user, get=True)
            user_group = user.message.replace(' ', '-')
            if user_group in remember_group:
                text_answer = bot.bot_say_schedule(bot, remember_group[user_group], data['time'])
            else:
                text_answer = bot.bot_say_schedule(bot, user_group, data['time'])

            if (not text_answer or text_answer == 'Not found group') and data['attempt'] == 1:
                bot.bot_say(help_request_user('group'))
                with open(path_wait_user + str(user.id) + '.wait.txt', 'w') as f:
                    json.dump({'timeout': time.time(), 'wait_label': 'group', 'attempt': 2, 'time': data['time']}, f)
                return
            elif (not text_answer or text_answer == 'Not found group') and data['attempt'] == 2:
                bot.bot_say('Так бывает, что люди не понимают друг друга... рил ток синк эбаут ит')
                os.remove(path_wait_user + str(user.id) + '.wait.txt')
                return

            bot.bot_say(text_answer)
            save_command_for_user(user)
            os.remove(path_wait_user + str(user.id) + '.wait.txt')
            return


def get_schedule(user, bot, result):
    if 'time_label' in result:
        result_time_label = result['time_label']
    else:
        bot.bot_say('Хорошо. На какой день?')
        with open(path_wait_user + str(user.id) + '.wait.txt', 'w') as f:
            json.dump({'timeout': time.time(), 'wait_label': 'time', 'attempt': 1}, f)
        return

    from .database import get_user_command
    remember_group = get_user_command(user)
    if not remember_group:
        bot.bot_say('Уточни номер группы.')
    else:
        bot.bot_say('Уточни номер группы или выбери позицию из предложенных мной: \n{}'.format(remember_group))
    with open(path_wait_user + str(user.id) + '.wait.txt', 'w') as f:
        for k, time_label in enumerate(result_time_label):
            if time_label in norm_date_day:
                result_time_label[k] = norm_date_day[time_label]
        json.dump({'timeout': time.time(), 'wait_label': 'group', 'attempt': 1, 'time': result_time_label}, f)
    return


logging.basicConfig(format='%(message)s [%(asctime)s] ', filename=path_bot322 + 'log.txt')


def report(user, bot, error_name, api):
    if os.path.exists(path_wait_user + str(user.id) + '.wait.txt'):
        os.remove(path_wait_user + str(user.id) + '.wait.txt')

    with open_to_flow(filename=path_bot322 + 'save_error.txt', lock_file=path_bot322 + 'lock_for_error.txt') as f:
        for er in f.readlines():
            if er.find(str(error_name)) != -1:
                bot.bot_say('По данной команде у меня обнаружен баг. \
                                                  Приношу свои извинения. Скоро все будет работать.')
                return

    bot.bot_say('Извините, у меня возникла ошибка. Я уже уведомил начальство.')
    logging.exception(msg='_' * 100 + '\n' + 'user_id: {} | message: {}'.format(user.id, user.message))
    time_error = datetime.datetime.today().time().strftime('%H:%M:%S')

    with open_to_flow(filename=path_bot322 + 'save_error.txt', mode='a',
                      lock_file=path_bot322 + 'lock_for_error.txt') as f:

        add_text_error = str(error_name) + ' | ' + str(time_error) + \
                         ' [user: {user}, message: {message}]\n'.format(user=user.id, message=user.message)
        f.write(add_text_error)

        api.messages.send(user_id=admin_id, message=add_text_error.strip())
        return