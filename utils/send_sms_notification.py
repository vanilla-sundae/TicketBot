from twilio.rest import Client
import os

def send_sms_notification(body):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")
    to_phone = os.getenv("TO_PHONE_NUMBER")
    
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body=body,
            from_=from_phone,
            to=to_phone
        )
        print(f"SMS sent to {to_phone}: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        raise e
