import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email_notification(subject, body):
    from_email = os.getenv("FROM_EMAIL_ADDRESS")
    from_password = os.getenv("FROM_EMAIL_PASSWORD")
    to_email = os.getenv("TO_EMAIL_ADDRESS")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()
    
    print(f"Email sent to {to_email}")
