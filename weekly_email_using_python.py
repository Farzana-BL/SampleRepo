# Import modules
from calendar import week
import smtplib, ssl
## email.mime subclasses
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
## The pandas library is only for generating the current date, which is not necessary for sending emails
import pandas as pd
import os
# Define the HTML document
weekly_info_html = open('weekly_info.html', 'r').read()
daywise_summary_info_html = open('daywise_summary_info.html', 'r').read()

# Set up the email addresses and email_password. Please replace below with your email address and email_password
email_sender = os.environ["EMAIL_SENDER"]
email_password = os.environ["EMAIL_PASSWORD"]
email_receiver = os.environ["EMAIL_RECEIVER"]
email_host_server=os.environ["EMAIL_HOST_SERVER"]
email_port=os.environ["EMAIL_PORT"]

# Generate today's date to be included in the email Subject
date_str = pd.Timestamp.today().strftime('%Y-%m-%d')

# Create a MIMEMultipart class, and set up the From, To, Subject fields
email_message = MIMEMultipart()
email_message['From'] = email_sender
email_message['To'] = email_receiver
email_message['Subject'] = f'Weekly Report Email - {date_str}'

# # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
email_message.attach(MIMEText(weekly_info_html, "html"))
email_message.attach(MIMEText(daywise_summary_info_html, "html"))

# email_message.add_header("Content-Type","text/html")
# email_message.add_header('Content-Disposition', 'attachment', filename=html)
# email_message.set_payload(html)
# # Convert it as a string
email_string = email_message.as_string() 
# Connect to the Gmail SMTP server and Send Email
context = ssl.create_default_context()
with smtplib.SMTP_SSL(email_host_server, email_port, context=context) as server:
   server.login(email_sender, email_password)
   server.sendmail(email_sender, email_receiver, email_string)
