profileData = {
  "result": true,
    "is_matched": true,
    "profile_email_match": false,
    "formattedInputName": "bondhushobha",
    "formattedEmail": "tanjimreza786@gmail.com",
    "profile_data": {
        "SerialNo": "",
        "NetflixEmail": "",
        "AccountStart": "Account Pass",
        "PackageName": "1 Screen",
        "ProfileName": "bondhushobha",
        "Email": "tanjimreza786@gmail.com",
        "PaidAmount": 250,
        "StartDate": "2024-03-19T18:15:00.000Z",
        "PaidForDays": 30,
        "EndDate": "2024-04-18T18:15:00.000Z",
        "DaysLeft": -18,
        "DaysRunning": 48,
        "Contact": "NewSend",
        "AccountEnds": "",
        "Remaining": "",
        "Password": "gglolxd585",
        "AccountEmail": "tanjim.netflix.01@gmail.com"
    }
}
const formattedEmail = profileData["formattedEmail"];
const formattedInputName = profileData["formattedInputName"];
var profile_email_match = false;
if (profileData["profile_data"]["Email"] === formattedEmail && profileData["profile_data"]["ProfileName"] === formattedInputName) {
                profile_email_match = true;
}

console.log(profile_email_match)