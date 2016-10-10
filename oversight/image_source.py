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

from datetime import datetime
from threading import Timer

from PIL import Image

from signals import image

logger = logging.getLogger('root')


class ImageSource(object):
    """
    ImageSource will generate a stream of image events.
    It periodically connects to a URL and downloads an image to generate each event.
    """

    def __init__(self, download_url, username=None, password=None, download_frequency=2.0, output_width=1000, output_height=565):
        self.download_url = download_url

        if username is not None:
            self.authorisation = (username, password)
        else:
            self.authorisation = None

        # Size of images to work with
        self.output_width = output_width
        self.output_height = output_height

        self.download_frequency = download_frequency

        Timer(self.download_frequency, self.get_image).start()

    def get_image(self):
        downloaded_image = None

        try:
            request = requests.get(self.download_url, auth=self.authorisation)

            if request.status_code is 200:
                downloaded_image = io.BytesIO(request.content)

        except requests.ConnectionError, e:
            logger.error("Connection Error:", e)
        except requests.HTTPError, e:
            logger.error("HTTP Error:", e)

        if downloaded_image is not None:
            resized_image = self.get_resized_image(downloaded_image)
            image.send(self, timestamp=datetime.utcnow(), image=resized_image)

        Timer(self.download_frequency, self.get_image).start()

    def get_resized_image(self, image_input):
        """
        Given a raw image from an image source, resize it to a standard size. Doing this results in more consistent
        results against the training set.

        :param image_input: A buffer with the raw image data.
        :return: Resized image data in jpeg format.
        """
        image = Image.open(image_input)
        resized_image = image.resize((self.output_width, self.output_height))

        output_buffer = io.BytesIO()
        resized_image.save(output_buffer, 'jpeg')

        return output_buffer.getvalue()
