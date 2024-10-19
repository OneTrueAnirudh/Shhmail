import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('gmail_token.json'):
        creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('gmail_credentials.json', SCOPES)
            flow.run_local_server(port=51043, access_type='offline')  # Request offline access
            creds = flow.credentials
        with open('gmail_token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def main():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    
    # Example: List the user's Gmail labels
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

if __name__ == '__main__':
    main()
