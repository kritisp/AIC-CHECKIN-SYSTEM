function onFormSubmit(e) {
  // Replace with your live Render backend URL
  var backendUrl = "https://aic-checkin-system.onrender.com/register"; 

  // The responses from the form
  var responses = e.namedValues;
  
  // Helper to safely get the first value of an array if it exists
  function getVal(key) {
    return responses[key] ? responses[key][0] : "";
  }
  
  // Extract values based on EXACT column names in Google Sheet
  // Note: "Email Address" is usually the default for auto-collected emails
  var name = getVal("Full Name") || getVal("Full Name ");
  var email = getVal("Email Address") || getVal("Email ID");
  var phone = getVal("Mobile Number");
  
  // Profession -> Role
  // Options: Student, Academician, Industrialist, Others
  var profession = getVal("Select your Profession") || "Delegate"; 
  
  // College/Organisation (can be in different sections)
  var college = getVal("Name of the Institute ") || getVal("Name of the Institute") || getVal("Name of the Organisation");
  
  var regNum = getVal("Registration Number");

  // We map 'Profession' to the 'role' field in the backend
  var payload = {
    "name": name,
    "email": email,
    "phone": phone,
    "role": profession,
    "college": college,
    "registration_number": regNum
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };

  try {
    UrlFetchApp.fetch(backendUrl, options);
    Logger.log("Successfully sent to backend: " + email);
  } catch (error) {
    Logger.log("Error sending to backend: " + error);
  }
}
