import pandas as pd
import json
from .settings import *
from .basic_functions import open_to_flow
from collections import OrderedDict


def logging_user(user):
        with open_to_flow(path_bot322 + 'Base.csv') as f:
            base = pd.read_csv(f, sep='\t', encoding='utf8')

        if user.id in base['user_id'].values:
            return 0

        user.get_name()
        import datetime
        new_user = {'Name': user.first_name + ' ' + user.last_name,
                    'user_id': user.id,
                    'time': datetime.datetime.today().strftime('%d.%m.%y %H:%M:%S'),
                    'command': json.dumps({})
                    }
        base = base.append(new_user, ignore_index=True)

        with open_to_flow(path_bot322 + 'Base.csv', 'w') as f:
            base.to_csv(f, index=False, sep='\t', encoding='utf8')
        return 1


def get_user_command(user, get=False):
    with open_to_flow(path_bot322 + 'Base.csv') as f:
        base = pd.read_csv(f, sep='\t', encoding='utf8')

    command = json.loads(base[base['user_id'] == user.id]['command'].values[0], object_hook=OrderedDict)
    if get:
        return command

    if not command:
        return None

    text_with_group = ''
    for ordinal in sorted(command, key=lambda x: int(x)):
        text_with_group += str(ordinal) + '. ' + str(command[ordinal]) + '\n'
    return text_with_group


def save_command_for_user(user):
    if user.message.isdigit():
        return
    with open_to_flow(path_bot322 + 'Base.csv') as f:
        base = pd.read_csv(f, sep='\t', encoding='utf8')

    group_presence = json.loads(base[base['user_id'] == user.id]['command'].values[0],
                                encoding='utf8', object_hook=OrderedDict)
    if not (user.message.replace(' ', '-') in group_presence.values()):
        group_presence[str(len(group_presence) + 1)] = user.message.replace(' ', '-')
        base['command'].loc[base['user_id'] == user.id] = json.dumps(group_presence)

        with open_to_flow(path_bot322 + 'Base.csv', 'w') as f:
            base.to_csv(f, index=False, sep='\t', encoding='utf8')
    return
