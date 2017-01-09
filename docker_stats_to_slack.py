from urllib.request import urlopen, Request, HTTPError, URLError
import os
import json
import docker
from multiprocessing import Pool
from datetime import datetime

HOOK_URL =  os.environ['SLACK_WEBHOOK_URL']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
SLACK_USERNAME = os.environ['SLACK_USERNAME']
SLACK_ICON_EMOJI = os.environ['SLACK_EMOJI']
PERCENTAGE_MEMORY = os.environ['MEMORY_PERCENTAGE']
PERCENTAGE_CPU = os.environ['CPU_PERCENTAGE']
SLEEP_TIME = os.environ['SLEEP_TIME']

client = docker.APIClient(base_url='unix://var/run/docker.sock')
client_env = docker.from_env()

def calculate_cpu_percent(d):
    """
    Taken from Docker Go Client:
    https://github.com/docker/docker/blob/28a7577a029780e4533faf3d057ec9f6c7a10948/api/client/stats.go#L309
    """
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                   float(d["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent

def humanize_bytes(bytesize, precision=2):
    """
    Humanize byte size figures
    https://gist.github.com/moird/3684595
    """
    abbrevs = (
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'bytes')
    )
    if bytesize == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytesize >= factor:
            break
    if factor == 1:
        precision = 0
    return '%.*f %s' % (precision, bytesize / float(factor), suffix)

def post_to_slack(message):
    slack_message = {"channel": SLACK_CHANNEL, "username": SLACK_USERNAME, "text": message, "icon_emoji": SLACK_ICON_EMOJI}
    req = Request(HOOK_URL, json.dumps(slack_message).encode("utf-8"))
    try:
        response = urlopen(req)
        response.read()
    except HTTPError as e:
        print(repr(e))
    except URLError as e:
        print(repr(e))

def get_docker_stats(container):
    try:    
        print(container.name)

        last_memory_post = None            
        last_cpu_post = None
        for x in client.stats(container.name,decode=True):
            cpu_p = calculate_cpu_percent(x)
            m_usage = humanize_bytes(x['memory_stats']['usage'])
            m_limit = humanize_bytes(x['memory_stats']['limit'])

            percentage_m_usage = (x['memory_stats']['usage'] / x['memory_stats']['limit']) * 100

            '''
            #if you want to print something
            print('{} : {}'.format(container.name,x['read']))
            print('{} : Cpu usage {} %'.format(container.name, cpu_p))
            print('{} : Memory Usage {}'.format(container.name, m_usage))
            print('{} : Memory limit {}'.format(container.name, m_limit))
            '''

            seconds_from_last_cpu_post = None
            if last_cpu_post:
                seconds_from_last_cpu_post = (datetime.now() - last_cpu_post).total_seconds()
            
            seconds_from_last_memory_post = None
            if last_memory_post:
                seconds_from_last_memory_post = (datetime.now() - last_memory_post).total_seconds()

            formatted_time = datetime.strptime(x['read'][:-4], "%Y-%m-%dT%H:%M:%S.%f").strftime('%Y-%m-%d %H:%M:%S')

            if (percentage_m_usage > float(PERCENTAGE_MEMORY)) and (seconds_from_last_memory_post is None or  seconds_from_last_memory_post > int(SLEEP_TIME)):
                last_memory_post = datetime.now()
                post_to_slack(':warning: {} :package: Container: *{}* - High memory used *{}*, limit *{}* :warning:'.format(formatted_time, container.name, m_usage, m_limit))
            if (cpu_p > float(PERCENTAGE_CPU)) and (seconds_from_last_cpu_post is None or  seconds_from_last_cpu_post > int(SLEEP_TIME)):
                last_cpu_post = datetime.now()
                post_to_slack(':warning: {} :package: Container: *{}* - High Cpu usage *{}* % :warning:'.format(formatted_time, container.name, round(cpu_p, 3)))

    except Exception as e:
        print(repre(e))

if __name__ == '__main__':
    try:
        l = client_env.containers.list()
        pool = Pool(processes=len(l))
        r  = pool.map_async(get_docker_stats, l)
        r.wait()
    except Exception as e:
        print(e)
