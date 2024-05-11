function doGet(e) {
  // Check if the profileName parameter exists
  if (!e.parameter.profileName || !e.parameter.email) {
    return ContentService.createTextOutput(
      JSON.stringify({result: false, message: "Profile name or email parameter is missing"})
    ).setMimeType(ContentService.MimeType.JSON);
  }

  const profileName = e.parameter.profileName; 
  const email = e.parameter.email;

  const formattedInputName = profileName.toLowerCase().replace(/\s/g, '');
  const formattedEmail = email.toLowerCase().replace(/\s/g, '');

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var profileNameColumn = 5;  // Column index for 'ProfileName'
  var startRow = 2;           // Assuming data starts from row 2
  var lastRow = sheet.getLastRow();
  var range = sheet.getRange(startRow, profileNameColumn, lastRow - startRow + 1);
  var profileNames = range.getValues();  // Read all values in the 'ProfileName' column
  var is_matched = false;
  var profile_email_match = false;
  
  for (var i = 0; i < profileNames.length; i++) {
      var sheetProfileName = profileNames[i][0].toLowerCase().replace(/\s/g, '');

      if (formattedInputName === sheetProfileName) {
        is_matched = true;
        var rowIndex = i + startRow;
        var rowData = sheet.getRange(rowIndex, 1, 1, 15).getValues()[0];
        var profileData = {
          SerialNo: rowData[0],
          NetflixEmail: rowData[1],
          AccountStart: rowData[2],
          PackageName: rowData[3],
          ProfileName: rowData[4].toLowerCase().replace(/\s/g, ''),
          Email: rowData[5].toLowerCase().replace(/\s/g, ''),
          PaidAmount: rowData[6],
          StartDate: rowData[7],
          PaidForDays: rowData[8],
          EndDate: rowData[9],
          DaysLeft: rowData[10],
          DaysRunning: rowData[11],
          Contact: rowData[12],
          AccountEnds: rowData[13],
          Remaining: rowData[14]
        };
        // Fetching password field information
        var result = 6 - (rowIndex % 7);
        var PasswordField = result + rowIndex;
        var PasswordFieldValue = sheet.getRange(PasswordField, 3).getDisplayValue();

        var AccountEmail = PasswordField - 4;
        var AccountEmailValue = sheet.getRange(AccountEmail, 2).getDisplayValue();

        // Adding password and account email to the response
        profileData.Password = PasswordFieldValue;
        profileData.AccountEmail = AccountEmailValue;

        if (profileData["Email"] === formattedEmail && profileData["ProfileName"] === formattedInputName) {
            profile_email_match = true;
          }

    }
  }

  return ContentService.createTextOutput(
    JSON.stringify({
      result: true, 
      is_matched: is_matched,
      profile_email_match: profile_email_match,
      formattedInputName: formattedInputName, 
      formattedEmail: formattedEmail, 
      profile_data: profileData,
  })).setMimeType(ContentService.MimeType.JSON);
}



