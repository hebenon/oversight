# Copyright 2016 Ben Carson. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
__author__ = 'bcarson'

import smtplib

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from signals import trigger_event, image_buffer

COMMASPACE = ', '


class SmtpNotifier(object):
    """
    A notification sink that sends notifications via smtp.
    """
    def __init__(self, from_address, recipients, smtp_server, username=None, password=None):
        self.smtp_server = smtp_server
        self.username = username
        self.password = password
        self.from_address = from_address
        self.recipients = recipients

        trigger_event.connect(self.handle_trigger_event)

    def handle_trigger_event(self, sender, **data):
        # Retrieve the image buffer, and add the event image, if not there.
        images = self.get_image_buffer()
        event_image = data['image']

        if event_image not in images:
            images = [event_image] + images

        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = 'Event: %s' % data['event']

        # Set addresses
        msg['From'] = self.from_address
        msg['To'] = COMMASPACE.join(self.recipients)
        msg.preamble = msg['Subject']

        for image in images:
            # Open the files in binary mode.  Let the MIMEImage class automatically
            img = MIMEImage(image)
            msg.attach(img)

        # Send the email via our own SMTP server.
        s = smtplib.SMTP_SSL(self.smtp_server)
        s.sendmail(self.from_address, self.recipients, msg.as_string())
        s.quit()

    def get_image_buffer(self):
        image_set = []
        for (receiver, return_value) in image_buffer.send(self):
            image_set.extend(return_value)

        return image_set