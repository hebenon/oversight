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

import calendar
import mock
import requests

from datetime import datetime, timedelta

from blinker import ANY
from nose.tools import with_setup

from oversight.pushover_notifier import PushoverNotifier
from oversight.signals import trigger_event

from test_utils import load_image


def teardown():
    # Disconnect any triggers
    for receiver in trigger_event.receivers_for(ANY):
        trigger_event.disconnect(receiver)


@with_setup(teardown=teardown)
@mock.patch('requests.post')
def test_send_notification(mock_requests):
    pushover_user = 'test_user'
    pushover_token = 'test_token'
    pushover_device = 'test_device'

    pushover_notifier_instance = PushoverNotifier(pushover_user=pushover_user,
                                                  pushover_token=pushover_token,
                                                  pushover_device=pushover_device)

    # Set up test conditions
    now = datetime.utcnow()
    test_image = load_image()
    test_prediction = 'test event'
    test_source = 'test_source'

    trigger_event.send('test', prediction=test_prediction, probability=0.95, timestamp=now, image=test_image, source=test_source)

    # Verify result
    assert mock_requests.call_count == 1
    assert mock_requests.call_args[1]['data']['user'] == pushover_user
    assert mock_requests.call_args[1]['data']['token'] == pushover_token
    assert mock_requests.call_args[1]['data']['timestamp'] == calendar.timegm(now.timetuple())
    assert test_prediction in mock_requests.call_args[1]['data']['message']
    assert test_source in mock_requests.call_args[1]['data']['message']
