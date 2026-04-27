function onFormSubmit(e) {
  // Replace with your live Render backend URL
  var backendUrl = "https://aic-checkin-system.onrender.com/register"; 

  // The responses from the form
  var responses = e.namedValues;
  
  // Helper to safely get the first non-empty value of an array 
  // (Crucial for handling duplicate column names like "Name of the Institute ")
  function getVal(key) {
    if (!responses[key]) return "";
    for (var i = 0; i < responses[key].length; i++) {
      if (responses[key][i] && responses[key][i].trim() !== "") {
        return responses[key][i].trim();
      }
    }
    return "";
  }
  
  // Extract values based on EXACT column names in the Google Sheet
  var name = getVal("Full Name") || getVal("Full Name ");
  
  // Prioritize manually typed Email ID, fallback to Google's Auto-collected Email Address
  var email = getVal("Email ID") || getVal("Email Address");
  
  var phone = getVal("Mobile Number");
  
  // Profession -> Role (Student, Academician, Industrialist, Others)
  var profession = getVal("Select your Profession") || "Delegate"; 
  
  // College/Organisation (can be in different sections depending on category)
  var college = getVal("Name of the Institute ") || getVal("Name of the Institute") || getVal("Name of the Organisation") || getVal("Organisation Name");
  
  var regNum = getVal("Registration Number") || getVal("Registration Number (for Students)");

  // Map everything to the payload expected by your backend
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
