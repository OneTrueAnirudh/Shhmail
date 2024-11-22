from g4f.client import Client
import time
import re

import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

def filter_emails_by_keywords(keywords_file, emails):
    """
    Filters emails based on whether they contain any of the tracked keywords.
    
    Args:
    - keywords_file (str): Path to a .txt file containing tracked keywords, one per line.
    - emails (list): List of email texts to filter.

    Returns:
    - filtered_emails (list): List of emails containing any tracked keywords.
    """
    # Read the keywords from the file and store them in a set
    with open(keywords_file, 'r') as file:
        tracked_keywords = set([line.strip().lower() for line in file.readlines()])

    filtered_emails = []

    for email in emails:
        # Convert the email text to lowercase for case-insensitive comparison
        email_lower = email.lower()
        
        # Check if any of the keywords are in the email text
        if any(keyword in email_lower for keyword in tracked_keywords):
            filtered_emails.append(email)

    return filtered_emails

def extract_deadlines(emails):
    """
    Processes a list of email texts in batches of 10 using an LLM.
    Extracts deadlines and corresponding event titles.
    """
    prompt_template = (
        "You are an assistant that extracts deadlines from emails. "
        "For each email below, identify 1 single deadline mentioned (with date and time specified)"
        "Additionally, provide a short title for a google calendar event based on the email."
        "Your response should contain only the deadline and title, and should be in the format:"
        "yyyy-mm-dd hh:mm event_title_1"
        "and so on for further mails (deadline separated from title by space, newline for each mail)"
        "If no deadline exists, respond with 'None'"
        "Here are the emails:\n\n{text}"
    )

    client = Client()
    results = []

    print("[INFO] Starting email processing...")

    for batch_start in range(0, len(emails), 3):
        print(f"[DEBUG] Processing batch starting at index {batch_start}...")

        batch = emails[batch_start:batch_start + 3]
        batch_prompt = "\n---\n".join([f"Email {i + 1}:\n{email}" for i, email in enumerate(batch)])
        prompt = prompt_template.format(text=batch_prompt)

        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                print(f"[DEBUG] Sending batch {batch_start} to LLM...")
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )

                # Extract LLM output
                llm_output = response.choices[0].message.content if hasattr(response, 'choices') else str(response)
                print(f"[DEBUG] LLM output for batch {batch_start}:\n{llm_output}")
                break
            except Exception as e:
                print(f"[ERROR] Error processing batch {batch_start}: {e}. Retrying...")
                retry_count += 1
                time.sleep(5)
        else:
            print(f"[ERROR] Failed to process batch starting at {batch_start}. Skipping...")
            continue

        # Improved parsing logic to handle deadlines and titles
        for line in llm_output.split("\n"):
            if line.strip():
                # Regex to capture a date in 'yyyy-mm-dd hh:mm' format
                match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+(.*)", line.strip())
                if match:
                    deadline = match.group(1)
                    title = match.group(2).strip()
                else:
                    # If no deadline is found, mark as "None"
                    deadline, title = "None", line.strip()

                results.append({
                    "email_index": batch_start + len(results) + 1,
                    "deadline": deadline,
                    "title": title,
                })
                print(f"[INFO] Processed email {batch_start + len(results)}: Deadline: {deadline}, Title: {title}")

    print("[INFO] Email processing complete.")
    return results

# Example usage
# if __name__ == "__main__":
#     # Example list of email texts
#     email_list = [
#         "Reminder: Project submission is due on 2024-11-25 at 10:00 AM.",
#         "Meeting scheduled for November 23rd, 2024 at 3:00 PM.",
#         "No deadlines in this email.",
#         # Add more email texts...
#     ]
#     filtered_email_list=filter_emails_by_keywords('keywords.txt',email_list)
#     extracted_results = extract_deadlines(filtered_email_list)
#     for result in extracted_results:
#         print(f"Email {result['email_index']}: Deadline: {result['deadline']}, Title: {result['title']}")
