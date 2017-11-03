# coding: utf-8

import requests, os, datetime, re, copy
from bs4 import BeautifulSoup
from .settings import *


def get_link_group(url, name_group, what_day):
    if requests.get(url).ok == False:
        return '404'

    link = get_link_level_education(url, name_group)
    if link == None:
        return None
    if requests.get(link).ok == False:
        return '404'

    html = requests.get(link).text
    soup = BeautifulSoup(html)
    rows = soup.find('div', id='page-content-wrapper').find_all('div', class_='row')[-1]
    for k, col in enumerate(rows.find_all('div', class_='col-sm-2')):
        if col.get_text().strip() != '':
            for item_group in col.div.find_all('a'):
                if item_group.text.split()[0] == name_group:
                    link_group = os.path.split(url)[0] + item_group.get('href')
                    force_quit = False
                    break
                else:
                    force_quit = True
        if force_quit == False:
            break

    if force_quit:
        return None

    count_week = (what_day - start_even).days // 7 + 1
    if count_week % 2 == 0:
        link_date = link_group + '?period=2'
    else:
        link_date = link_group + '?period=1'

    if requests.get(link_date).ok == False:
        return '404'

    return link_date


def get_link_level_education(url, name_group):
    if name_group in ['Б17-1И1', 'Б17-5И1', 'Б17-5И3', 'С17-1И2']:
        return link_for_moscow_obninsk

    html = requests.get(url).text
    soup = BeautifulSoup(html)
    table = soup.find('ul', class_='nav nav-tabs')

    for level_education in table.find_all('li'):
        if (level_education.a.get('title')[0] == name_group[0]) or \
                (level_education.a.get('title')[0] == name_group.replace('И', 'П')[0]):
            link = os.path.split(url)[0] + level_education.a.get('href')
            return link

    return None


def get_schedule(url, what_day, get_week):
    html = requests.get(url).text
    # with open('save_html.html', 'w', encoding='utf8') as f:
    #     f.write(html)

    soup = BeautifulSoup(html)
    content = soup.find('div', id='page-content-wrapper')

    days = content.find_all('h3')
    days = [day.text.replace('\n', '') for day in days]

    week_day_present = datetime.datetime.weekday(what_day)
    start_week_day = what_day - datetime.timedelta(days=week_day_present)
    schedule_total = {}
    for day, list_group in zip(days, content.div.find_all('div', class_='list-group')):

        # Если необходимо расписание на сутки, то освобождаем все лишние дни от парсинга
        if (get_week == False) and (week_day_present != weeks[day]):
            continue

        week_day_count = start_week_day + datetime.timedelta(days=weeks[day])
        time = []
        lesson = []
        audience = []
        label = []
        teacher = []
        for list_group_item in list_group.find_all('div', class_='list-group-item'):

            # found time
            time.append(list_group_item.find('div', class_='lesson-time').text.replace('\xa0', ' '))

            sublesson = []
            sublabel = []
            subaudience = []
            subteacher = []
            for list_lesson in list_group_item.find('div', class_='lesson-lessons'). \
                    find_all('div', class_='lesson'):

                try:
                    lesson_date = re.sub('[()\xa0]', '',
                                         list_lesson.find('span', class_='lesson-dates').text).strip().split('—')
                    ld1 = [int(x) for x in lesson_date[0].split('.')[::-1]]
                    ld2 = [int(x) for x in lesson_date[1].split('.')[::-1]]
                    lesson_start_date = datetime.date(ld1[0], ld1[1], ld1[2])
                    lesson_end_date = datetime.date(ld2[0], ld2[1], ld2[2])
                    if (lesson_start_date > week_day_count) or (week_day_count > lesson_end_date):
                        continue
                except AttributeError:
                    pass

                # found labels
                try:
                    sublabel.append(list_lesson.find('div', class_='label label-default label-lesson').text)
                except AttributeError:
                    sublabel.append('Not found label')

                # found lessons
                list_tag_delete = copy.copy(list_lesson)
                tags = ['div', 'span', 'a', 'i']
                for tag in tags:
                    for k in range(len(list_tag_delete.find_all(tag))): list_tag_delete.find(tag).decompose()
                sublesson.append(list_tag_delete.text.replace(',', '').strip().split('\n\n'))

                # found teachers
                list_tag_delete = copy.copy(list_lesson)
                tags = ['div', 'span', 'i']
                for tag in tags:
                    for k in range(len(list_tag_delete.find_all(tag))): list_tag_delete.find(tag).decompose()
                y = [x.text.replace('\xa0', ' ') for x in list_tag_delete.find_all('', class_='text-nowrap')]
                if y == []: y.append('Not found teacher')
                subteacher.append(y)

                # found audience
                try:
                    list_audience_tag_delete = copy.copy(list_lesson.find('div', class_='pull-right'))
                    for _ in list_audience_tag_delete.find_all('a', class_='btn-map'):
                        list_audience_tag_delete.find('a', class_='btn-map').decompose()
                    # z = [x.text for x in list_lesson.find('div', class_='pull-right').find_all('a')]
                    z = [x.text for x in list_audience_tag_delete.find_all('a')]
                    if z == []: z.append('Not found audience')
                except AttributeError:
                    z = ['Not found audience']
                # subaudience.append(list(filter(None,z)))
                subaudience.append(z)

            audience.append(subaudience)
            lesson.append(sublesson)
            label.append(sublabel)
            teacher.append(subteacher)

        # create dictionary for time, label, lesson ...
        schedule_day = {'time': time,
                        'label': label,
                        'lesson': lesson,
                        'teacher': teacher,
                        'audience': audience
                        }

        # create dictionary for day
        schedule_total[day] = schedule_day

    if schedule_total == {}:
        return 'Not found lessons'
    else:
        return schedule_total


def schedule(name_group, what_day, get_week):
    if what_day < start_even:
        return 'No lessons'

    search_group_link = get_link_group(url_main, name_group, what_day)
    if search_group_link == None:
        return 'Not found group'
    elif search_group_link == '404':
        return 'Server error'
    else:
        schedule = get_schedule(search_group_link, what_day, get_week)

    return schedule