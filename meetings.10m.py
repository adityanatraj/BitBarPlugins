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


def main():
    """Shows basic usage of the Google Calendar API.

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
    print '[{}{}]'.format(u'\U0001F310', len(events))
    print '---'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        tm = datetime.datetime.strptime(start[0:-6], '%Y-%m-%dT%H:%M:%S')
        h = tm.hour - 12 if tm.hour > 12 else tm.hour
        m = str(tm.minute).zfill(2)
        print '{}:{} {} | href={}'.format(h, 
                                          m,
                                          event['summary'], 
                                          event['hangoutLink'])

if __name__ == '__main__':
    main()
