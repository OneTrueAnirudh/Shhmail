import os.path
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']

def authenticate_calendar():
    creds = None
    if os.path.exists('calendar_token.json'):
        creds = Credentials.from_authorized_user_file('calendar_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('calendar_credentials.json', SCOPES)
            creds = flow.run_local_server(port=51043,access_type='offline')  # Use a different port if needed
        with open('calendar_token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def main():
    creds = authenticate_calendar()
    service = build('calendar', 'v3', credentials=creds)
    
    # Get the current time in UTC
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()  # Use timezone-aware datetime
    print('Getting the upcoming 10 events')
    events_result = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

if __name__ == '__main__':
    main()
