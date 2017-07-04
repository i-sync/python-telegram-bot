#!/usr/lib/env python

import urllib.request
import urllib.error
import logging
import json
import gzip
import re
from io import BytesIO

#file path
voice_path = 'files/voice'
photo_path = 'files/photo'

#synchronized bot
token = '317386823:xxxxxxxx'
command_list = ['help', 'start', 'weather', 'joke', 'gif', 'me']
command_str = \
'''
/weather get the weather info
/joke   get a joke
/gif    get a random gif
/me     get my info
'''

proxy = 'http://127.0.0.1:8123'

#SSH
ssh_server = 'www.lifetime.photo'
ssh_port = 22
ssh_username = 'pi'
ssh_password = 'xxxxx'
ssh_path = '/home/pi/tmp'

#api url
weather_url = 'http://wthrcdn.etouch.cn/weather_mini?citykey=101010100'
gif_url ='http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC'
joke_url = 'http://api.icndb.com/jokes/random/'

def get_weather():
    reg = r'[\u4E00-\u9FA5 ]'
    request = urllib.request.Request(weather_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'})
    try:
        res = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        logging.error(e.info())
        return 'get weather data failed, please try again later...'

    data = res.read()
    if (('Content-Encoding' in res.info()) and (res.info()['Content-Encoding'] == 'gzip')):
        # data=zlib.decompress(data, 16+zlib.MAX_WBITS)
        data = gzip.decompress(data)
        data = str(data, 'utf-8')

    json_data = json.loads(data)

    status = json_data['status']

    if (status == 1000):
        wdata = json_data['data']
        city = wdata['city']
        aqi = int(wdata['aqi'])
        temperature = wdata['wendu']
        forecast = wdata['forecast'][0]
        date = forecast['date']
        weather = forecast['type']
        wind = forecast['fengli']
        direction = forecast['fengxiang']
        high = re.sub(reg, '', forecast['high'])
        low = re.sub(reg, '', forecast['low'])
        level = ''
        if (aqi <= 50 and aqi > 0):
            level = '优秀'
        elif (aqi <= 100 and aqi > 50):
            level = '良好'
        elif (aqi <= 150 and aqi > 100):
            level = '一般'
        elif (aqi <= 200 and aqi > 150):
            level = '很差'
        else:
            level = '很差'
        return '{},今天是{} {}, 空气质量:{}{},当前温度{}[{} ~ {} ],{}{}.'.format(city, date, weather, aqi, level, temperature, low,
                                                                      high, direction, wind)
    else:
        return 'get weather data failed, please try again later...'


def get_random_gif():
    request = urllib.request.Request(gif_url)

    try:
        res = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        logging.error(e.info())
        return None

    if res.getcode() == 200:
        json_data = json.loads(res.read().decode('utf-8'))
        if json_data['meta']['status'] == 200:
            img_url = json_data['data']['image_original_url']
            return img_url

    return None

def get_random_joke():
    request = urllib.request.Request(joke_url)
    try:
        res = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        logging.error(e.info())
        #logging.error(e.read())
        return 'get random joke failed, please try again later...'

    if res.getcode() == 200:
        json_data = json.loads(res.read().decode('utf-8'))
        if json_data['type'] == 'success':
            return json_data['value']['joke']

    return 'get random joke failed, please try again later...'
