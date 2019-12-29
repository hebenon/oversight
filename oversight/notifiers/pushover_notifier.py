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

import logging
import calendar

import requests

from oversight.signals import trigger_event, image_buffer

logger = logging.getLogger('root')

class PushoverNotifier(object):
    """
    A notification sink that sends notifications via pushover.
    """
    def __init__(self, pushover_user, pushover_token, pushover_device=None):
        self.pushover_user = pushover_user
        self.pushover_token = pushover_token
        self.pushover_device = pushover_device

        trigger_event.connect(self.handle_trigger_event)

    def handle_trigger_event(self, sender, **data):
        # Pushover doesn't support images, so just send the event.
        notification_data = {
            "user": self.pushover_user,
            "token": self.pushover_token,
            "message": "Camera %s, event: %s" % (data['source'], data['prediction']),
            "timestamp": calendar.timegm(data['timestamp'].timetuple())
        }

        # Optionally, set the device.
        if self.pushover_device:
            notification_data['device'] = self.pushover_device

        try:
            r = requests.post("https://api.pushover.net/1/messages.json", data=notification_data)

            if r.status_code != 200:
                logger.error("Failed to send notification, (%d): %s" % (r.status_code, r.text))
        except requests.ConnectionError as e:
            logger.error("Connection Error:", e)
        except requests.HTTPError as e:
            logger.error("HTTP Error:", e)

    def get_image_buffer(self):
        image_set = []
        for (receiver, return_value) in image_buffer.send(self):
            image_set.extend(return_value)

        return image_set