#!/usr/bin/python
#Calender
from __future__ import print_function
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
#Audio
import os
import sys
from gtts import gTTS
#Time
from dateutil.parser import parse
#Weather
from weather import Weather, Unit
#Quotes
import requests
import json

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

def main():
    #Calender auth
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    day_from_now = datetime.utcnow() + timedelta(hours=24)
    later = day_from_now.isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, timeMax=later, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    #Quote
    url = 'https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    result = requests.get(url, headers=headers)
    json_str = result.content.decode('utf-8')
    content = json.loads(json_str)
    quote = "Like the great have said, " + content["quoteText"]
    print(quote);

    #Date
    day = datetime.strftime(datetime.now(), "%A %B %d")
    print(day + '\nSchedule:')

    #Weather
    weather = Weather(unit=Unit.CELSIUS)
    lookup = weather.lookup(4177)
    condition = lookup.condition

    line = "Good Morning Cooper! Today is" + day + ". I looks like its going to be " + condition.text + " today."

    if not events:
        print('Nothing Today')
        line += "You have nothing scheduled for today."
    else:
        line += "Here is your schedule for today.";
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            dt = parse(start)
            print(dt.strftime("%I:%M %p"), event['summary'])
            line += "At " + dt.strftime("%I:%M %p") + " you will, " + event['summary']+ "."

    line += quote

    #play Audio
    tts = gTTS(text=line, lang='en')
    tts.save("reply.mp3")
    os.system("ffplay -loglevel -8 -autoexit reply.mp3")

if __name__ == '__main__':
    main()
