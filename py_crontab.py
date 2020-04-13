from crontab import CronTab
import json

from data import Data

def update_or_create_job(cron, funk, job_id, time_key):
    job_list = cron.find_comment(job_id)
    if len(job_list)==1:
        job = job_list[0]
    elif (len(job_list)>1)|(len(job_list)==0):
        for job in job_list:
            cron.remove(job)
        turn = ''
        if time_key=='start':
            turn='on'
        elif time_key=='end':
            turn='off'
        command_str = 'sh /home/pi/activate_timer_switch.sh {}.{}{}'.format(funk["remote"].lower(), funk["socket"], turn)
        job = cron.new(command=command_str, comment=job_id)
    times = funk[time_key].split(':')
    hour = int(times[0])
    minute = int(times[1])
    weekdays = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    weekdays_str = ''
    for i in range(len(weekdays)):
        if funk[weekdays[i]]==True:
            weekdays_str+='{},'.format(i)
    if len(weekdays_str)==0:
        cron.remove(job)
    else:
        weekdays_str = weekdays_str[:-1]
        set_all_str = '{} {} {} * *'.format(minute, hour, weekdays_str)
        job.setall(set_all_str)

    return cron

def update_timer_switches():
    cron = CronTab(user='pi')
    with open(Data.url) as file:
        data = json.load(file)

    socket_timer_disabled_list = list()

    for funk in data["funksteckdosen"]:
        if funk["timer_switch"]==False:
            socket_timer_disabled_list.append('socket_{}{}_on'.format(funk["remote"], funk["socket"]))
            socket_timer_disabled_list.append('socket_{}{}_off'.format(funk["remote"], funk["socket"]))

    current_jobs = [job.comment for job in cron]

    for socket_timer_disabled in socket_timer_disabled_list:
        job_list = cron.find_comment(socket_timer_disabled)
        if len(job_list)>0:
            for job in job_list:
                cron.remove(job)

    for funk in data["funksteckdosen"]:
        if funk["timer_switch"]==True:
            socket_timer_on = 'socket_{}{}_on'.format(funk["remote"], funk["socket"])
            socket_timer_off = 'socket_{}{}_off'.format(funk["remote"], funk["socket"])
            cron = update_or_create_job(cron, funk, socket_timer_on, 'start')
            cron = update_or_create_job(cron, funk, socket_timer_off, 'end')

    cron.write()



