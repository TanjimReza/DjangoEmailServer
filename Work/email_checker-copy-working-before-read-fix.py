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
from dotenv import load_dotenv

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
# Login to the central inbox
mail = imaplib.IMAP4_SSL(EMAIL_SERVER)
# mail = imaplib.IMAP4(EMAIL_SERVER)
mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
mail.select("inbox")


def try_except_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")

    return wrapper


@try_except_decorator
def get_email_body(message):
    """Extracts the email body from the message."""
    if message.is_multipart():
        # Iterate over each part
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode()
            elif (
                content_type == "text/html" and "attachment" not in content_disposition
            ):
                return part.get_payload(decode=True).decode()
    else:
        # Not a multipart email, just return the payload
        return message.get_payload(decode=True).decode()


@try_except_decorator
def get_login_otp_from_email(email_body):
    """Extracts the login OTP from the email body."""
    # Use regex to extract the login OTP

    pattern = r"Enter this code to sign in\s+(\d+)"
    match = re.search(pattern, email_body)
    if match:
        sign_in_code = match.group(1)
        print(f"Sign-in code: {sign_in_code}")
        return sign_in_code

    return None


@try_except_decorator
def get_household_url_profile(email_body):
    profile, get_code_url = None, None
    hi_pattern = r"Hi (.*?),"

    # Regular expression pattern to match the "Get Code URL"
    url_pattern = r"Get Code\s*<(https?://[\w/\.\-_\?=&%]+[^>]+)>"
    # Search for "Hi {Names Here}"
    hi_match = re.search(hi_pattern, email_body, re.DOTALL)
    if hi_match:
        profile = hi_match.group(1)

    # Search for the "Get Code URL"
    url_match = re.search(url_pattern, email_body, re.DOTALL)
    if url_match:
        get_code_url = url_match.group(1)
        print(f"Get Code URL: {get_code_url}")

    return profile, get_code_url

@try_except_decorator
def get_cleaned_email(email_address):
    email_pattern = r"<([^>]+@[^>]+)>"
    email_body = re.search(email_pattern, email_address).group(1)
    return email_body



def main():
    typ, messages = mail.search(None, EMAIL_FILTER)
    message_ids = messages[0].split()
    if not message_ids:
        # logging.info("No new emails", end="\n")
        print("No new emails", end="\n")
        return
    current_date_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Found {len(message_ids)} new emails", end=f" {current_date_time}\n")
    for idx, message_id in enumerate(message_ids):
        typ, data = mail.fetch(message_id, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        
        from_email = get_cleaned_email(decode_header(msg["From"])[0][0]) or decode_header(msg["From"])[0][0]
        to_email = decode_header(msg["To"])[0][0]
        
        
        date_time = parsedate_to_datetime(msg["Date"]).strftime("%Y-%m-%d %H:%M:%S")
        email_body = get_email_body(msg) or "Empty for now"
        
        login_otp = get_login_otp_from_email(email_body)
        profile, household_link = get_household_url_profile(email_body)
        tag = "OTHER"
        
        subject, subject_encoding = decode_header(msg["Subject"])[0]

        if subject_encoding is None:
            subject_str = subject
        else:
            subject_str = subject.decode(subject_encoding)
            
        print(f"Subject: {subject_str}")
        print(f"Subject Type: {type(subject_str)}")

        if "Your Netflix temporary access code".strip().replace(" ", "").lower() in subject_str.strip().replace(" ", "").lower():
            print("TEMP ACCESS")
            tag = "HOUSEHOLD"
        
        
        email_dict = {
            "from_email": from_email,
            "to_email": to_email,
            "subject": subject,
            "profile": profile,
            "date_time": date_time,
            "email_body": email_body,
            "login_otp": login_otp,
            "household_link": household_link,
            "tag": tag
        }
        if email_dict["login_otp"] is not None:
            email_dict["tag"] = "LOGIN"
        logging.info(f"Email Number #{idx + 1}")
        logging.info(f"Tag: {email_dict['tag']}")
        logging.info(f"Date-Time: {email_dict['date_time']}")
        logging.info(f"From: {email_dict['from_email']}")
        logging.info(f"To: {email_dict['to_email']}")
        logging.info(f"Subject: {email_dict['subject']}")
        logging.info(f"Profile: {email_dict['profile']}")
        logging.info(f"Login OTP: {email_dict['login_otp']}")
        logging.info(f"Household Link: {email_dict['household_link']}")
        logging.info(f"Email Body: {email_dict['email_body']}")
        logging.info("-" * 50)  # Separator for readability

        # Optionally, mark the message as read
        mail.store(message_id, "+FLAGS", "\\Seen")

    # Close the connection
    # mail.logout()


schedule.every(REFRESH_TIME_SECONDS).seconds.do(main)

while True:
    for i in range(REFRESH_TIME_SECONDS):
        print(
            f"Checking for new emails in {REFRESH_TIME_SECONDS - i} seconds", end="\r"
        )
        time.sleep(3)
    schedule.run_pending()
