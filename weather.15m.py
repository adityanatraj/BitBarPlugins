#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# requires: requests

# documentation for the forecast.io API is here:
# https://developer.forecast.io/docs/v2

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import json
import os
from datetime import datetime

ICON = {
    'clear-day': u'☀',
    'clear-night': u'☀',
    'rain': u'⛈',
    'snow': u'❄',
    'sleet': u'❄',
    'wind': u'☰',
    'fog': u'☁',
    'cloudy': u'☁',
    'partly-cloudy-day': u'⛅',
    'partly-cloudy-night': u'⛅',
}

BEARING = {
    0: ('↑', 'N'),
    1: ('↖', 'NW'),
    2: ('←', 'W'),
    3: ('↙', 'SW'),
    4: ('↓', 'S'),
    5: ('↘', 'SE'),
    6: ('→', 'E'),
    7: ('↗', 'NE'),
}


def clean_time(seconds):
    moment = datetime.fromtimestamp(seconds)
    return moment.strftime('%I:%M %p')


def temp_color(temp):
    if temp < 45:
        return 'blue'
    elif temp < 60:
        return 'yellow'
    else:
        return 'red'


def bearing(angle, nonsym=True):
    idx = int((angle + 22.5) / 45) % 8
    return BEARING[idx][nonsym]


def render_weather(weather):
    curStat = ICON[weather['currently']['icon']]
    curFeel = round(weather['currently']['temperature'])
    curTemp = round(weather['currently']['apparentTemperature'])
    print '{}°F {} | color={}'.format(curFeel,
                                      curStat,
                                      temp_color(curTemp))
    print '---'
    if curFeel != curTemp:
        print 'actually {}°F'.format(curTemp)
    if weather['currently']['icon'] in ('rain', 'snow'):
        print 'precip: {} in/hr'.format(weather['currently']['precipIntensity'])
    print 'wind: {} mph {}'.format(weather['currently']['windSpeed'],
                                   bearing(weather['currently']['windBearing']))
    if 'alerts' in weather:
        for alert in weather['alerts']:
            print '⚠ {} {} | color=yellow href={}'.format(alert['title'],
                                                          clean_time(alert['expires']),
                                                          alert['uri'])
    print 'lines | href=http://forecast.io/lines'


config_path = os.path.join(os.path.expanduser('~'), '.bitbar/weather.conf')
if not os.path.exists(config_path):
    print '⚠ | color=yellow'
    print '---'
    print 'create'
    print 'weather.conf'
    print 'in ~/.bitbar/'
    exit(0)
else:
    config = json.load(open(config_path, 'rU'))

params = {
    'units': 'us',  # also valid: si, us, uk, uk2
    'exclude': 'minutely,hourly,daily,flags',  # this runs every 15m anyway
}

url = 'https://api.forecast.io/forecast/{}/{},{}'.format(config['api_key'],
                                                         config['lat'],
                                                         config['lon'])

response = requests.get(url, params=params)

if response.status_code == 200:
    render_weather(response.json())
else:
    print '☉'
