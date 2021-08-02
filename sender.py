from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import yaml
from time import sleep
from threading import Thread

import serial


last_received = ''


def meta_loader():
    """Utility function to load email parameters."""

    with open('config.yml') as config:
        meta = yaml.load(config, Loader=yaml.FullLoader)

    return meta


def send_email(meta):
    """Utility function to send email to users from meta."""

    # Setup email configurations
    message = MIMEMultipart('alternative')
    message['Subject'] = meta['subject']
    message['From'] = meta['email']
    message['To'] = ", ".join(meta['recipients'])

    # Build email body
    html = "<h1>The oxygen level is low.<h1>"
    body = MIMEText(html, 'html')
    message.attach(body)

    # Create secure connection with server and send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(meta['email'], meta['password'])
    text = message.as_string()
    server.sendmail(meta['email'], meta['recipients'], text)
    server.quit()


def monitor_status():
    """Utility function to check the oxygen level."""

    # Load email meta data
    meta = meta_loader()

    # Check the oxygen level
    ser = serial.Serial(meta['com_port'], meta['port'], timeout=1)
    
    with ser:
        while True:
            # Read the serial port and parse data
            line = ser.readline()
            line = line.decode()
            line = line.strip()

            # Try to convert value to float
            try:
                value = float(line)
            except ValueError:
                value = 0
            print(value)
            
            # Check if the value is within the range
            if value < meta['o2_th'] and value != 0:
                send_email(meta)
                sleep(meta['sleep_time'])


if __name__ == '__main__':
    monitor_status()