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

import mock
import smtplib

from datetime import datetime, timedelta

from blinker import ANY
from nose.tools import with_setup

from oversight.smtp_notifier import SmtpNotifier
from oversight.signals import trigger_event

from test_utils import load_image


def teardown():
    # Disconnect any triggers
    for receiver in trigger_event.receivers_for(ANY):
        trigger_event.disconnect(receiver)


@with_setup(teardown=teardown)
@mock.patch('smtplib.SMTP_SSL')
def test_send_mail_to_recipients(mock_smtplib):
    from_address = 'Test <noreply@test.test>'
    recipients = ['first@test.test', 'second@test.test']
    smtp_server = 'smtp.test.test'

    smtp_notifier_instance = SmtpNotifier(from_address=from_address, recipients=recipients, smtp_server=smtp_server)

    # Set up test conditions
    now = datetime.utcnow()
    test_image = load_image()

    trigger_event.send('test', prediction='test event', probability=0.95, timestamp=now, image=test_image)

    # Verify result
    assert mock_smtplib.return_value.sendmail.call_count == 1
    mock_smtplib.return_value.sendmail.assert_called_with(from_address, recipients, mock.ANY)
