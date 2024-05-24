import email
import imaplib
import logging
import os
import re
import time
from email.header import decode_header
from email.utils import parsedate_to_datetime
from functools import wraps

import schedule
from background_task import background
from bandwidth_util_new import measure_bandwidth
# from django.conf import settings
from dotenv import load_dotenv

# from .models import Email

# Set up logging
logging.basicConfig(
    filename="email_checker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


load_dotenv()
EMAIL_SERVER = os.getenv("EMAIL_SERVER")
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FILTER = os.getenv("EMAIL_FILTER")
REFRESH_TIME_SECONDS = int(os.getenv("REFRESH_TIME_SECONDS"))
HOUSEHOLD_SUBJECT = os.getenv("HOUSEHOLD_SUBJECT")
LOGIN_SUBJECT = os.getenv("LOGIN_SUBJECT")


@measure_bandwidth
def check_emails():
    print("-" * 50)
    print(f"Connecting to {EMAIL_SERVER} with IMAP...")
    with imaplib.IMAP4_SSL(EMAIL_SERVER) as mail:
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        print("Checking inbox for unread emails....")
        print("-" * 50)

        # Search for unread emails
        result, data = mail.search(None, 'UNSEEN')
        if result != "OK":
            print("No unread emails found.")
            return

        mail_ids = data[0].split()
        print(f"Found {len(mail_ids)} unread emails")

        for index, email_id in enumerate(reversed(mail_ids)):
            result, data = mail.fetch(email_id, "(RFC822)")
            if result != "OK":
                print(f"Failed to fetch email ID {email_id}")
                continue

            raw_email = data[0][1]
            raw_email_string = raw_email.decode("utf-8")
            email_message = email.message_from_string(raw_email_string)

            # Decode the email subject
            subject, encoding = decode_header(email_message["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            print(f"#{index + 1} - Subject: {subject}")

            # Mark the email as read
            mail.store(email_id, '+FLAGS', '\\Seen')


check_emails()
