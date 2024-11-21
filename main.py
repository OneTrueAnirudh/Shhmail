from googleapiclient.discovery import build
from gmail_client import authenticate_gmail, get_unread_emails_with_retry
from calendar_client import validate_and_add_event
import tkinter as tk
from keyword_ui import KeywordTrackerApp
from LLM import extract_deadlines, filter_emails_by_keywords
import os

def process_emails():
    # Get unread mails into a list
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    # Get unread emails
    email_texts, unread_count = get_unread_emails_with_retry(service)
    print(f"Number of unread emails: {unread_count}")
    print(f"Number of email texts processed: {len(email_texts)}")

    # Pass the unread mails into an LLM for deadline extraction, scheduling calendar events in Google Calendar
    filtered_email_list = filter_emails_by_keywords('keywords.txt', email_texts)
    extracted_results = extract_deadlines(filtered_email_list)
    for result in extracted_results:
        print(f"Email {result['email_index']}: Deadline: {result['deadline']}, Title: {result['title']}")
        validate_and_add_event(result['deadline'], result['title'],service)

def delete_token_files():
    files_to_delete = ['calendar_token.json', 'gmail_token.json']

    for file_name in files_to_delete:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"{file_name} deleted successfully.")
            except Exception as e:
                print(f"Error deleting {file_name}: {e}")
        else:
            print(f"{file_name} does not exist.")

# Open the keyword tracker dialog box
root = tk.Tk()
app = KeywordTrackerApp(root)

# Use a button or event to trigger the email processing
def on_submit():
    process_emails()

# Bind the submit button to trigger the processing
app.submit_button.config(command=on_submit)

root.mainloop()  # This keeps the GUI running and pauses execution until submit

delete_token_files()
