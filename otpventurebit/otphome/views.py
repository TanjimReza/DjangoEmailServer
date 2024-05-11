import logging
from time import sleep

import requests
from background_task import background
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from .models import Email
from .tasks import check_emails, normalize_text

check_emails(repeat=settings.REFRESH_TIME_SECONDS)

# Create your views here.

logger = logging.getLogger(__name__)


def index(request):
    if request.method == 'POST' or request.method == 'GET':
        print(request.POST or request.GET)
        return render(request, 'otphome/index.html')
    return render(request, 'otphome/index.html')


def hx(request):
    check_profile_name = normalize_text(request.POST['profile_name'])
    check_profile_email = request.POST['profile_email'].strip().replace(
        " ", "")

    print(check_profile_name, check_profile_email)

    OTP_API_URL = settings.SHEET_ACCESS_KEY

    params = {

        'email': check_profile_email
    }
    result = None
    try:
        logger.debug("Trying to connect to OTP API with params: %s", params)
        response = requests.get(OTP_API_URL, params=params)
        result = response.json()
        LOGIN_EMAILS = None
        HOUSEHOLD_EMAILS = None
    except Exception as e:
        logger.error("Error connecting to OTP API: %s", e)
        return HttpResponse(f"Something went wrong: Contact VentureBit (Facebook/Email)")

    logger.debug("Response from OTP API: %s", result)
    try:
        if not result['valid_result']:
            logger.info("Invalid Email: %s", check_profile_email)
            return HttpResponse(f"Invalid Email: {check_profile_email}")

        logger.info("Valid Email: %s", check_profile_email)
        logger.info("Getting user data...")

        for each_profile in result['profileDataArray']:
            profile_name = normalize_text(each_profile['ProfileName'])
            account_email = each_profile['AccountEmail']

            logger.debug("Found Profile Name: %s", profile_name)
            logger.debug("Found Account Email: %s", account_email)

            if profile_name == check_profile_name:
                print(f"Profile Name Matched: {profile_name}")
                HOUSEHOLD_EMAILS = Email.get_most_recent_household_emails(
                    account_email,
                    profile_name=profile_name,
                    count=3
                )

                LOGIN_EMAILS = Email.get_most_recent_login_emails(
                    account_email,
                    count=3
                )

                logger.debug(f"Found {len(HOUSEHOLD_EMAILS)} Household Emails")
                logger.debug(f"Found {len(LOGIN_EMAILS)} Login Emails")

                return render(request, 'otphome/partials/combined_otp_household.html', {'otp_emails': LOGIN_EMAILS, 'household_emails': HOUSEHOLD_EMAILS})
    except Exception as e:
        logger.error("Error after OTP API Request: %s", e)

    return HttpResponse("Error processing your request. Contact Support!")
