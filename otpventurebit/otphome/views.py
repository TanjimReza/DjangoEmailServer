from time import sleep

import requests
from background_task import background
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from .models import Email
from .tasks import check_emails, normalize_text, get_cleaned_email

check_emails(repeat=settings.REFRESH_TIME_SECONDS)

# Create your views here.


def index(request):
    if request.method == 'POST' or request.method == 'GET':
        print(request.POST or request.GET)
        return render(request, 'otphome/index.html')
    return render(request, 'otphome/index.html')


def hx(request):
    check_profile_name = normalize_text(request.POST['profile_name'])
    check_profile_email = get_cleaned_email(request.POST['profile_email'])
    
    print(check_profile_name, check_profile_email)
    OTP_API_URL = settings.SHEET_ACCESS_KEY

    params = {

        'email': check_profile_email
    }
    params['email'] = "mezbah.rahman20@gmail.com"
    try:
        response = requests.get(OTP_API_URL, params=params)
        result = response.json()
        LOGIN_EMAILS = None
        HOUSEHOLD_EMAILS = None
        
        if result['result']:
            profiles_for_this_email = len(
                result['profileDataArray'])
            print("🚆 ~ views.py:40 -> profiles_for_this_email: ",profiles_for_this_email)
            
            for each_profile in result['profileDataArray']:
                profile_name = normalize_text(each_profile['ProfileName'])
                account_email = get_cleaned_email(each_profile['AccountEmail'])
            

    except Exception as e:
        print(f"Error from OTP API: {e}")
        return HttpResponse(f"Error from OTP API: Contact Support! {e}")

    # if result['profile_email_match']:
    #     try:
    #         account_email = result.get(
    #             'profile_data', {}).get('AccountEmail', '')
    #
    #
    # otp_emails = Email.get_most_recent_otp_emails(account_email, 3)
    #         household_emails = Email.get_most_recent_household_emails(
    #             account_email, 3)
    #
    #
    # print(otp_emails)
    #         print(household_emails)
    #         print(f"Emails received from Email Database")
    #         print(f"Generating HTML View")
    #         return render(request, 'otphome/partials/combined_otp_household.html', {'otp_emails': otp_emails, 'household_emails': household_emails})

    #     except Exception as e:
    #         print(f"Error from OTP API: {e}")
    #         return HttpResponse(f"Error from Email Database: Contact Support!")

    # else:
    #     print("Profile & Email mismatch! Invalid User!")
    #     result = 'Profile & Email mismatch! Invalid User!'
    return HttpResponse(result)
