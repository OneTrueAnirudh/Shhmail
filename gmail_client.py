import os.path
import base64
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import html2text
from googleapiclient.errors import HttpError
import time
import random

# If modifying these SCOPES, delete the file token.json.
SCOPES = SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('gmail_token.json'):
        creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('gmail_credentials.json', SCOPES)
            flow.run_local_server(port=51043, access_type='offline')
            creds = flow.credentials
        with open('gmail_token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def clean_html_content(html_content):
    """
    Convert HTML content to plain text using html2text.
    """
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True  # Skip hyperlinks in the email
    text_maker.ignore_images = True  # Ignore images (optional)
    text_maker.ignore_emphasis = True  # Ignore asterisks and underscores around text
    return text_maker.handle(html_content)

def remove_recurring_text(email_text):
    """
    Remove recurring disclaimers or institutional text from the email body.
    """
    recurring_patterns = [
        r">>\s\*\*Vellore Institute of Technology.*?\*\*",  # Matches VIT rankings
        r"_\*\*Disclaimer:.*?$",  # Matches the disclaimer and everything after
        r"^.*\*\*Disclaimer:.*?$",  # Matches disclaimers at the start
        r"\*{2,}",  # Removes all occurrences of ** (bold symbols)
        r"\n\s*\n",  # Removes multiple newlines
        r"[^\S\n]*[>\-=_\*]+\s*"  # Removes excessive symbols like * > - _ = from the text
    ]
    for pattern in recurring_patterns:
        email_text = re.sub(pattern, "", email_text, flags=re.DOTALL | re.MULTILINE)
    return email_text.strip()

def exponential_backoff_with_jitter(base=2, cap=60):
    """
    Exponential backoff with jitter for retrying after errors.
    """
    delay = base + random.uniform(0, base)
    return min(delay, cap)

def extract_email_body(payload):
    """
    Extract the email body from the payload, handling multiple parts if necessary.
    """
    if 'body' in payload and payload['body'].get('data'):
        try:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            return None

    if 'parts' in payload:
        email_body = ""
        for part in payload['parts']:
            part_body = extract_email_body(part)
            if part_body:
                email_body += part_body
        return email_body
    return None

def get_unread_emails_with_retry(service):
    email_texts = []
    unread_count = 0
    processed_ids = set()
    page_token = None
    while True:
        try:
            unread_messages = service.users().messages().list(
                userId='me', labelIds=['INBOX'], q="is:unread", pageToken=page_token).execute()
            messages = unread_messages.get('messages', [])
            unread_count += len(messages)

            for message in messages:
                if message['id'] in processed_ids:
                    continue
                processed_ids.add(message['id'])

                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg.get('payload', {})
                email_text = extract_email_body(payload)

                if email_text:
                    email_text = clean_html_content(email_text)
                    cleaned_text = remove_recurring_text(email_text)
                    email_texts.append(cleaned_text)
                else:
                    print(f"Skipped email ID: {message['id']} due to missing or unreadable body.")

            page_token = unread_messages.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            if error.resp.status == 429:  # Too many requests error
                print("Rate limited, retrying after a delay...")
                delay = exponential_backoff_with_jitter()
                time.sleep(delay)
            else:
                raise

    return email_texts, unread_count

def mark_email_as_read(service, message_id):
    """Marks the email as read by removing the 'UNREAD' label."""
    try:
        service.users().messages().modify(
            userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}
        ).execute()
        #print(f"Marked email {message_id} as read.")
    except HttpError as error:
        print(f"Error marking email {message_id} as read: {error}")

def get_unread_emails_with_retry(service):
    email_texts = []
    unread_count = 0
    processed_ids = set()
    page_token = None
    while True:
        try:
            unread_messages = service.users().messages().list(
                userId='me', labelIds=['INBOX'], q="is:unread", pageToken=page_token).execute()
            messages = unread_messages.get('messages', [])
            unread_count += len(messages)

            for message in messages:
                if message['id'] in processed_ids:
                    continue
                processed_ids.add(message['id'])

                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg.get('payload', {})
                email_text = extract_email_body(payload)

                if email_text:
                    email_text = clean_html_content(email_text)
                    cleaned_text = remove_recurring_text(email_text)
                    email_texts.append(cleaned_text)
                    # Mark the email as read after processing
                    mark_email_as_read(service, message['id'])
                else:
                    print(f"Skipped email ID: {message['id']} due to missing or unreadable body.")

            page_token = unread_messages.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            if error.resp.status == 429:  # Too many requests error
                print("Rate limited, retrying after a delay...")
                delay = exponential_backoff_with_jitter()
                time.sleep(delay)
            else:
                raise

    return email_texts, unread_count