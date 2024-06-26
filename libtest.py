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
from django.conf import settings
from dotenv import load_dotenv

from .models import Email

# Set up logging
logging.basicConfig(
    filename="email_checker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

EMAIL_SERVER = settings.EMAIL_SERVER
EMAIL_ACCOUNT = settings.EMAIL_ACCOUNT
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
EMAIL_FILTER = settings.EMAIL_FILTER
REFRESH_TIME_SECONDS = settings.REFRESH_TIME_SECONDS
HOUSEHOLD_SUBJECT = settings.HOUSEHOLD_SUBJECT
LOGIN_SUBJECT = settings.LOGIN_SUBJECT


def try_except_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")

    return wrapper


def get_email_body(message):
    logger.debug(":::: Inside get_email_body()")
    try:
        if message.is_multipart():
            logger.debug("Email is multipart")
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
            return message.get_payload(decode=True).decode()
    except Exception as e:
        logger.error(f"Error in get_email_body: {e}")


def get_login_otp_from_email(email_body):
    """Extracts the login OTP from the email body."""
    logger.debug(":::: Inside get_login_otp_from_email()")
    try:
        pattern = r"Enter this code to sign in\s+(\d+)"
        match = re.search(pattern, email_body)
        if match:
            logger.debug("-- OTP Found")
            sign_in_code = match.group(1)
            print(f"-- OTP: {sign_in_code}")
            return sign_in_code
        return None
    except Exception as e:
        logger.error(f"Error in get_login_otp_from_email: {e}")


def get_household_url_from_email(email_body):
    logger.debug(":::: Inside get_household_url_from_email()")
    try:
        get_code_url = None
        # Regular expression pattern to match the "Get Code URL"
        # url_pattern = r"Get Code\s*<(https?://[\w/\.\-_\?=&%]+[^>]+)>"
        url_pattern = r"Get Code\s*\[?(https?://[\w/\.\-_\?=&%]+[^>\]\s]+)"
        # Search for the "Get Code URL"
        url_match = re.search(url_pattern, email_body, re.DOTALL)
        if url_match:
            logger.debug("-- Link Found")
            get_code_url = url_match.group(1)
            print(f"-- Get Code URL: {get_code_url}")
        return get_code_url
    except Exception as e:
        logger.error(f"Error in get_household_url_from_email: {e}")


def get_profile_name_from_email(email_body):
    """Extracts the profile name from the email body."""
    logger.debug(":::: Inside get_profile_name_from_email()")
    try:
        profile = None
        hi_pattern = r"Hi (.*?),"
        hi_match = re.search(hi_pattern, email_body, re.DOTALL)
        if hi_match:
            profile = hi_match.group(1)
            print(f"Profile: {profile}")
            logger.debug("-- Profile:", profile)
        return profile
    except Exception as e:
        logger.error(f"Error in get_profile_name_from_email: {e}")


def get_cleaned_email(email_address):
    try:
        email_pattern = r"<([^>]+@[^>]+)>"
        email_body = re.search(email_pattern, email_address).group(1)
        return email_body
    except Exception as e:
        logger.error(f"Error in get_cleaned_email: {e}")


def save_email_to_db(email_data):
    #! Very Important
    try:
        logger.error("TRYING TO SAVE", email_data)
        new_email = Email.objects.create(
            from_email=email_data["from_email"],
            to_email=email_data["to_email"],
            subject=email_data["subject"],
            profile=normalize_text(
                email_data["profile"]) if email_data["profile"] else None,
            date_time=email_data["date_time"],
            body=email_data["email_body"],
            login_otp=email_data["login_otp"],
            household_link=email_data["household_link"],
            tag=email_data["tag"]
        )
        new_email.save()
        logger.debug(f"Saved email to database: {new_email}")
    except Exception as e:
        logger.error(f"Error in save_email_to_db: {e}")

    print(f"Saved email to database: {new_email}")


def normalize_text(text: str):
    try:
        text = text.lower()  # ? Convert to lowercase
        text = text.strip()  # ? Remove leading/trailing whitespace
        text = text.replace(" ", "")  # ? Remove spaces
        text = text.replace(":", "")  # ? Remove colons
        text = text.replace(".", "")  # ? Remove dots
        text = text.replace("-", "")  # ? Remove dashes
        text = text.replace("_", "")  # ? Remove underscores
        text = text.replace("(", "")  # ? Remove parentheses
        text = text.replace(")", "")  # ? Remove parentheses
        text = text.replace("?", "")  # ? Remove slashes
        return text
    except Exception as e:
        logger.error(f"Error in normalize_text: {e}")


@background(schedule=settings.REFRESH_TIME_SECONDS)
def check_emails():
    logger.error("Inside CheckEmails")
    with imaplib.IMAP4_SSL(EMAIL_SERVER) as mail:
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        try:
            typ, messages = mail.search(None, EMAIL_FILTER)
            message_ids = messages[0].split()

            # ? If there are no new emails, return
            if not message_ids:
                logger.error("No new emails found.")
                return
            # * If there are new emails, fetch them
            for idx, message_id in enumerate(message_ids):
                try:
                    # ? Peeking, RFC822 by defualt marks as read
                    typ, data = mail.fetch(message_id, "(BODY.PEEK[])")

                    msg = email.message_from_bytes(data[0][1])

                    # ? Sender Email
                    from_email = get_cleaned_email(
                        # ! No idea why wrote like this
                        decode_header(msg["From"])[0][0]
                    ) or decode_header(msg["From"])[0][0]

                    # ? Receiver Email
                    to_email = decode_header(msg["To"])[0][0]

                    # ? Formatted Date-Time Object for better management
                    date_time = parsedate_to_datetime(
                        msg["Date"]).strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    logger.error(f"Error in fetching email: {e}")
                    logger.error(f"Message ID: {message_id}")
                    continue

                try:
                    email_body = get_email_body(msg)
                except Exception as e:
                    logger.error(f"Error in get_email_body: {e}")
                    email_body = "EMPTY EMAIL BODY"

                # ? Email Subject: Can be used to determine Email TAG (OTHER, LOGIN, HOUSEHOLD)
                subject, subject_encoding = decode_header(msg["Subject"])[0]

                # print(f"Subject: {subject}")
                logger.info("-"*30)
                logger.info(f"Email #{idx + 1}")
                logger.info(f"Subject: {subject}")

                tag = None  # ? By default None - HOUSEHOLD, LOGIN
                profile = None
                login_otp = None
                household_link = None

                if normalize_text(LOGIN_SUBJECT) in normalize_text(subject):
                    tag = "LOGIN"
                    logger.info("Tag: LOGIN")
                    login_otp = get_login_otp_from_email(email_body)
                    #! Marking as read
                    mail.store(message_id, "+FLAGS", "\\Seen")

                elif normalize_text(HOUSEHOLD_SUBJECT) in normalize_text(subject):
                    tag = "HOUSEHOLD"
                    logger.info("Tag: HOUSEHOLD")
                    profile = get_profile_name_from_email(email_body)
                    household_link = get_household_url_from_email(email_body)
                    #! Marking as read
                    mail.store(message_id, "+FLAGS", "\\Seen")
                else:
                    logger.info("Tag: OTHER")
                    logger.debug(f"Subject mismatch: {subject}")

                email_data = {
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
                # print("Going to check emails")
                if email_data["tag"] == "HOUSEHOLD" or email_data["tag"] == "LOGIN":
                    try:
                        print(f"Email saving: {email_data['tag']}, {
                              email_data['profile']}")
                        save_email_to_db(email_data)
                    except Exception as e:
                        logger.error(f"Error in save_email_to_db: {e}")
                else:
                    # print(f"Email not saved: {email_data['tag']}")
                    # ? logger Email Data (except email_body)
                    log_dict = {k: v for k, v in email_data.items()
                                if k != "email_body"}
                    logger.info(f"Email Data: {log_dict}")

        except Exception as e:
            print(f"Exception from check_emails: {e}")
