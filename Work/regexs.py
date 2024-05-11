import re 

email = "Venture Bit <venturebitbd.12@gmail.com>"
def get_cleaned_email(email_address):
    # Clean up the email body
    email_pattern = r"<([^>]+@[^>]+)>"
    
    email_body = re.search(email_pattern, email_address).group(1)

    print(f"Email body: {email_body}")
    return email_body

get_cleaned_email(email)