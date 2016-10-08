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

import requests
import io
import logging

logger = logging.getLogger('root')


class ImageSource(object):
    """
    ImageSource will generate a stream of image events.
    It periodically connects to a URL and downloads an image to generate each event.
    """

    def __init__(self, download_url, username, password):
        self.download_url = download_url

        if username is not None:
            self.authorisation = (username, password)
        else:
            self.authorisation = None

    def get_image(self):
        try:
            request = requests.get(self.download_url, auth=self.authorisation)

            if request.status_code is 200:
                return io.BytesIO(request.content)

        except requests.ConnectionError, e:
            logger.error("Connection Error:", e, request)
        except requests.HTTPError, e:
            logger.error("HTTP Error:", e, request)

        return None
