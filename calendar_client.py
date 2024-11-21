import os.path
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_calendar():
    creds = None
    if os.path.exists('calendar_token.json'):
        creds = Credentials.from_authorized_user_file('calendar_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('calendar_credentials.json', SCOPES)
            creds = flow.run_local_server(port=51043, access_type='offline')  # Use a different port if needed
        with open('calendar_token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_event(service, title, event_datetime):
    # Convert user-provided datetime to ISO 8601 format with timezone awareness
    event_time = datetime.datetime.strptime(event_datetime, "%Y-%m-%d %H:%M").astimezone()
    event_time_iso = event_time.isoformat()

    # Define event details
    event = {
        'summary': title,
        'start': {'dateTime': event_time_iso, 'timeZone': 'UTC'},
        'end': {'dateTime': (event_time + datetime.timedelta(hours=1)).isoformat(), 'timeZone': 'UTC'},  # Default 1-hour duration
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': 12 * 60}],  # Reminder 12 hours before
        },
    }

    # Insert event into primary calendar
    created_event = service.events().insert(calendarId='primary', body=event).execute()

    # Print confirmation message
    print(f"Event '{title}' scheduled for {event_datetime}. Reminder set 12 hours prior!")

def add_event(event_datetime,title):
    creds = authenticate_calendar()
    service = build('calendar', 'v3', credentials=creds)
    create_event(service, title, event_datetime)

def validate_and_add_event(deadline, title, service):
    """
    Validates the deadline format and creates a calendar event if valid.
    """
    try:
        # Ensure the deadline matches the expected format
        event_time = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        # Call create_event if deadline is valid
        add_event(deadline, title)
    except ValueError:
        print(f"[ERROR] Invalid deadline format: {deadline}. Skipping event creation for title: {title}.")

#add_event('test-2','2024-11-21 10:30') # datetime in 'yyyy-mm-dd hh:mm' format