import json

with open('demo.json') as f:
    data = json.load(f)
    profile_data = data.get('profileDataArray', None)
    for profile in profile_data:
        profile_ = {
            "profile_name": profile.get('ProfileName'),
            "profile_email": profile.get('Email'),
            "profile_started": profile.get('StartDate'),
            "profile_ends": profile.get('EndDate'),
            "days_left": profile.get('DaysLeft'),
            "netflix_email": profile.get('AccountEmail'),
            "netflix_password": profile.get('Password'),
        }
        print(profile_)
