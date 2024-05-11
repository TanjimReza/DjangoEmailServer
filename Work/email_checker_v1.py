import email
import os
import imaplib
from email.header import decode_header
from email.utils import parsedate_to_datetime
import time
from dotenv import load_dotenv
import schedule

load_dotenv()
EMAIL_SERVER = os.getenv("EMAIL_SERVER")
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# Login to the central inbox
# mail = imaplib.IMAP4_SSL(EMAIL_SERVER)
mail = imaplib.IMAP4_SSL(EMAIL_SERVER)
mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
mail.select("inbox")  # You can change this if OTPs are moved to a specific folder
# Search for unread emails# Search for all emails
typ, messages = mail.search(None, "(UNSEEN)")
message_ids = messages[0].split()


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


def main():
    typ, messages = mail.search(None, "(UNSEEN)")
    message_ids = messages[0].split()

    if not message_ids:
        print("No new emails", end="\r")
        return

    for idx, message_id in enumerate(message_ids):
        typ, data = mail.fetch(message_id, "(RFC822)")  # Fetch the email by ID

        # Parse the email into a message object
        msg = email.message_from_bytes(data[0][1])
        email_dict = {
            "from": decode_header(msg["From"])[0][0],
            "to": decode_header(msg["To"])[0][0],
            "Subject": decode_header(msg["Subject"])[0][0],
            "Profile": "Empty for now",  # Placeholder for additional data
            "Date_Time": parsedate_to_datetime(msg["Date"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Email_Body": get_email_body(msg),
        }

        # Print formatted email data
        print(f"Email Number #{idx + 1}")
        print("From:", email_dict["from"])
        print("To:", email_dict["to"])
        print("Subject:", email_dict["Subject"])
        print("Date-Time:", email_dict["Date_Time"])
        print("Email Body:", email_dict["Email_Body"].strip())
        print("-" * 50)  # Separator for readability

        # Optionally, mark the message as read
        # mail.store(message_id, "+FLAGS", "\\Seen")

    # Close the connection
    # mail.logout()


schedule.every(1).seconds.do(main)
while True:
    for i in range(1):
        # print checking for new emails in i seconds
        print(f"Checking for new emails in {1-i} seconds ", end="\r")
        time.sleep(1)
    schedule.run_pending()

# if __name__ == "__main__":
#     main()
