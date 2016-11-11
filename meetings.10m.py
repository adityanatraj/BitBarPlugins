#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.bitbar/.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        secret_path = os.path.join(credential_dir, CLIENT_SECRET_FILE)
        flow = client.flow_from_clientsecrets(secret_path, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
    return credentials


class Event(object):

    class When(object):
        @staticmethod
        def parse_time_raw(start):
            if 'dateTime' in start:
                startTime = start['dateTime'][0:-6]
                tm = datetime.datetime.strptime(startTime, '%Y-%m-%dT%H:%M:%S')
                h = tm.hour - 12 if tm.hour > 12 else tm.hour
                m = str(tm.minute).zfill(2)
                tm_str = '{}:{}'.format(h, m)
            elif 'date' in start:
                tm_str = None
            else:
                tm_str = start
            return tm_str

        def __init__(self, start):
            self.all_day = False
            self.when = None
            self.parse_time(start)

        def parse_time(self, start):
            tm = Event.When.parse_time_raw(start)
            if tm is None:
                self.all_day = True
                self.when = ''
            else:
                self.all_day = False
                self.when = tm

        def __str__(self):
            return '' if self.all_day else self.when

    @staticmethod
    def parse_summary(raw_event):
        return raw_event['summary'].strip()
    
    @staticmethod
    def parse_link(raw_event):
        link = raw_event.get('htmlLink', None)
        link = raw_event.get('hangoutLink', link)
        return link

    def __init__(self, raw_event):
        self.when = Event.When(raw_event['start'])
        self.summary = Event.parse_summary(raw_event)
        self.link = Event.parse_link(raw_event)

    def __str__(self):
        when_prefix = str(self.when)
        if when_prefix:
            when_prefix += ' '
        link_suffix = ' | href={}'.format(self.link) if self.link else ''
        return '{}{}{}'.format(when_prefix, self.summary, link_suffix)

class Calendar(object):
    def __init__(self):
        self.daily = []
        self.timed = []

    def add_event(self, event):
        if event.when.all_day:
            self.daily.append(event)
        else:
            self.timed.append(event)

    def __str__(self):
        num_events = len(self.daily) + len(self.timed)
        title = '[{}{}]'.format(num_events, u'\u231B')
        header = '---'
        daily_events = '\n'.join('{}'.format(e) for e in self.daily)
        header = '---'
        timed_events = '\n'.join('{}'.format(e) for e in self.timed)
        output = '{}\n{}\n{}\n{}'.format(title, header, daily_events, timed_events)
        return output

def main():
    """
    Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # 'Z' indicates UTC time
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    eod = (datetime.datetime.utcnow() + datetime.timedelta(hours=12)).isoformat() + 'Z'

    eventsResult = service.events().list(calendarId='primary',
                                         timeMin=now,
                                         timeMax=eod,
                                         maxResults=5,
                                         singleEvents=True,
                                         orderBy='startTime').execute()

    events = eventsResult.get('items', [])

    calendar = Calendar()
    for event in events:
        calendar.add_event(Event(event))

    print(calendar)

if __name__ == '__main__':
    main()
