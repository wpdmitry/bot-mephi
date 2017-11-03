# coding: utf-8

import datetime, re
from .settings import *
from .parse_schedule import schedule


def answer_to_r(bot, name_group, time_label):
    if time_label in norm_date_day:
        time_label = norm_date_day[time_label]
    if time_label == 'СЕГОДНЯ':
        what_day = datetime.date.today()
        get_week = False
        if datetime.date.weekday(what_day) == 6:
            return 'Сегодня можешь отдохнуть.'
    elif time_label == 'ЗАВТРА':
        what_day = datetime.date.today() + datetime.timedelta(days=1)
        get_week = False
        if datetime.date.weekday(what_day) == 6:
            return 'Завтра у тебя выходной.'
    elif time_label == 'НЕДЕЛЯ':
        what_day = datetime.date.today()
        get_week = True
    elif time_label in choose_day.keys():
        if time_label == 'ВС':
            return 'В этот день можешь отдохнуть.'
        day_week_now = datetime.date.weekday(datetime.date.today())
        day_week_then = weeks[choose_day[time_label]]
        if  day_week_then >= day_week_now:
            difference = day_week_then - day_week_now
            what_day = datetime.date.today() + datetime.timedelta(days=difference)
        else:
            difference = 7 - (day_week_now - day_week_then)
            what_day = datetime.date.today() + datetime.timedelta(days=difference)
        get_week = False
    else:
        return

    result = schedule(name_group=name_group, what_day=what_day, get_week=get_week)
    if type(result) is str:
        return result

    text = ['_' * 30]
    # text = '_' * 30 + '\n'
    for key in list_day_week:
        try:
            day = result[key]
        except KeyError:
            continue
        text.append(key)
        # text += key + '\n'
        text.append('_' * 30)
        # text += '_' * 30 + '\n'
        for time, label, lesson, teacher, audience in \
                zip(day['time'], day['label'], day['lesson'], day['teacher'], day['audience']):

            text.append('&#127891;' + ' ' + str(time))
            # text += '&#127891;' + ' ' + str(time) + '\n'
            lesson_and_label_count = [str(x) + ':' + ' ' + re.sub("[\[\]']", '', str(y)) + '\n' for x, y in zip(label, lesson)]
            teacher_count = [re.sub("[\[\]']", '', str(x) + '\n') for x in teacher]
            audience_count = [re.sub("[\[""\]']", '', str(x) + '\n') for x in audience]
            for les, teach, aud in zip(lesson_and_label_count, teacher_count, audience_count):
                text.append((les + teach + aud).rstrip())
                # text += les + teach + aud
        text.append('_' * 30)
        # text += '_' * 30 + '\n'
    return '\n'.join(text)
    # return text