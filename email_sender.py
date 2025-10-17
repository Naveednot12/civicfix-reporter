import requests
import base64
import os

# --- 1. Configuration ---
# IMPORTANT: Paste the API key you just generated from Brevo here.
API_KEY = os.environ.get("BREVO_API_KEY") 
# This is the email address that will send the reports.
# It MUST be the same email you used to sign up for Brevo.
SENDER_EMAIL = "naveed12092004@gmail.com"
SENDER_NAME = "CivicFix Reporter Bot"


# --- 2. The Main Function ---
def send_report_email(to_email, subject, body, photo_bytes):
    """
    Sends an email with a photo attachment using the Brevo API.
    'photo_bytes' should be the raw byte content of the image file.
    """
    api_url = "https://api.brevo.com/v3/smtp/email"
    
    # The headers are for authentication.
    headers = {
        "accept": "application/json",
        "api-key": API_KEY,
        "content-type": "application/json",
    }

    # We must convert the photo's raw bytes into a special text format
    # called base64. This is the standard way to send files in JSON.
    encoded_photo = base64.b64encode(photo_bytes).decode()

    # This is the "payload" or the body of our request to the API.
    # It's a dictionary that describes the email we want to send.
    data = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": f"<html><body>{body}</body></html>",
        "attachment": [{"name": "issue_report.jpg", "content": encoded_photo}]
    }

    try:
        # Make the POST request to the Brevo API to send the email.
        response = requests.post(api_url, headers=headers, json=data)
        
        # Brevo returns status code 201 for a successful send.
        if response.status_code == 201:
            print(f"Successfully sent email to {to_email}")
            return True
        else:
            # If it fails, print the error message from Brevo.
            print(f"Failed to send email. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
        return False


# --- 3. Testing Block ---
if __name__ == "__main__":
    # IMPORTANT: Change this to your own email address for testing.
    TEST_RECIPIENT_EMAIL = "naveed12092004@gmail.com"
    
    print(f"Sending a test email to {TEST_RECIPIENT_EMAIL}...")

    try:
        # Open a test image file from your project folder in "read binary" mode.
        with open("test_image.jpg", "rb") as image_file:
            test_photo_bytes = image_file.read()

        test_subject = "This is a Test Report"
        test_body = """
        <h1>Civic Issue Report</h1>
        <p>This is a test of the email sending system.</p>
        <p>Location: Test Location, 123 Test St.</p>
        """

        send_report_email(
            to_email=TEST_RECIPIENT_EMAIL, 
            subject=test_subject, 
            body=test_body, 
            photo_bytes=test_photo_bytes
        )
    except FileNotFoundError:
        print("\nERROR: Could not find 'test_image.jpg' in the project folder.")
        print("Please add a small JPG image named 'test_image.jpg' to test the email sender.")