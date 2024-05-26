from datetime import datetime
import pytz
import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from otphome.models import BandwidthLog, Email
from otphome.utils.email_utils import normalize_text
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import BandwidthLogSerializer, EmailSerializer


def convert_date(date):
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    target_timezone = pytz.timezone(settings.TIME_ZONE)
    converted_date = date.astimezone(target_timezone)
    return converted_date.strftime('%d-%b-%Y')


@api_view(['GET'])
def getDatanew(request):
    data = BandwidthLog.objects.all()
    data = BandwidthLogSerializer(data, many=True)
    return Response(data.data)


@api_view(['POST'])
def submit_email(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Redirect to the profile selection view with the provided email
    return Response({"message": "Email submitted successfully.", "email": email}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_profiles(request, email):
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    OTP_API_URL = settings.SHEET_ACCESS_KEY
    params = {'email': email}

    try:
        response = requests.get(OTP_API_URL, params=params)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not result.get('valid_result', False):
        return Response({"error": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)

    profiles = [
        {
            "profile_name": profile.get('ProfileName'),
            "profile_email": profile.get('Email'),
            "account_email": profile.get('AccountEmail')
        }
        for profile in result.get('profileDataArray', [])
    ]
    print(profiles)

    return Response({"profiles": profiles}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_profile_details(request, email, profile_name):
    OTP_API_URL = settings.SHEET_ACCESS_KEY

    email = email

    print(email, profile_name)

    params = {'email': email}

    try:
        response = requests.get(OTP_API_URL, params=params)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not result.get('valid_result', False):
        return Response({"error": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)

    matched_profiles = [
        profile for profile in result.get('profileDataArray', [])
        if normalize_text(profile.get('ProfileName')) == normalize_text(profile_name) and profile.get('Email') == email
    ]

    if not matched_profiles:
        return Response({"error": "No matching profiles found."}, status=status.HTTP_404_NOT_FOUND)

    profile_details = matched_profiles[0]

    # Assuming you have methods to fetch the emails
    household_emails = Email.get_most_recent_household_emails(
        profile_details.get('AccountEmail'), profile_name=profile_name, count=3
    )
    login_emails = Email.get_most_recent_login_emails(
        profile_details.get('AccountEmail'), count=3
    )
    household_emails = EmailSerializer(household_emails, many=True).data
    login_emails = EmailSerializer(login_emails, many=True).data
    # print(profile_details)
    result = {
        "profile_name": profile_details.get('ProfileName'),
        "profile_email": profile_details.get('Email'),
        "profile_start_date": profile_details.get('StartDate'),
        "profile_end_date": convert_date(profile_details.get('EndDate')),
        "days_left": profile_details.get('DaysLeft'),
        "account_email": profile_details.get('AccountEmail'),
        "emails": {
            "household_emails": household_emails,
            "login_emails": login_emails
        }
    }
    print(result)
    return Response(
        result, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def getUserData(request):
    if request.method == 'POST':
        user_email = request.data.get('email', None)
        user_profile = request.data.get('profile', None)
        OTP_API_URL = settings.SHEET_ACCESS_KEY
        params = {

            'email': 'tanjimreza786@gmail.com'
        }
        response = requests.get(OTP_API_URL, params=params)
        result = response.json()

        profile_data = result.get('profileDataArray', None)
        result_arr = []
        for profile in profile_data:
            profile_ = {
                "profile_name": profile.get('ProfileName'),
                "profile_email": profile.get('Email'),
                "profile_started": profile.get('StartDate'),
                "profile_ends": profile.get('EndDate'),
                "days_left": profile.get('DaysLeft'),
                "netflix_email": profile.get('AccountEmail'),
                "netflix_password": profile.get('Password'),
                "status": "None"
            }

            if 0 < profile_.get("days_left") <= 3:
                profile_["status"] = "Renew Required"
            elif profile_.get("days_left") == 0:
                profile_["status"] = "Last day to Renew"
            elif profile_.get("days_left") < 0:
                profile_["status"] = "Expired"
            else:
                profile_["status"] = "Active"

            result_arr.append(profile_)

        return Response(result_arr)

    return Response({"success": True})
