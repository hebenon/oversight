__author__ = 'bcarson'

import smtplib

# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

COMMASPACE = ', '

class SmtpNotifier(object):
    def __init__(self, from_address, smtp_server, username=None, password=None):
        self.smtp_server = smtp_server
        self.username = username
        self.password = password
        self.from_address = from_address

    def send_notification(self, event, images, recipients):
        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = 'Event: %s' % event

        # Set addresses
        msg['From'] = self.from_address
        msg['To'] = COMMASPACE.join(recipients)
        msg.preamble = msg['Subject']

        for image in images:
            # Open the files in binary mode.  Let the MIMEImage class automatically
            img = MIMEImage(image)
            msg.attach(img)

        # Send the email via our own SMTP server.
        s = smtplib.SMTP_SSL(self.smtp_server)
        s.sendmail(self.from_address, recipients, msg.as_string())
        s.quit()

