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

from datetime import datetime, timedelta

from blinker import ANY
from nose.tools import with_setup

from oversight.signals import image, image_buffer
from oversight.image_buffer import ImageBuffer

from test_utils import load_image


def get_image_buffer():
    image_set = []
    for (receiver, return_value) in image_buffer.send('test'):
        image_set.extend(return_value)

    return image_set


def teardown():
    # Disconnect any triggers
    for receiver in image.receivers_for(ANY):
        image.disconnect(receiver)

    for receiver in image_buffer.receivers_for(ANY):
        image_buffer.disconnect(receiver)

@with_setup(teardown=teardown)
def test_return_images_if_less_than_length():
    image_buffer_instance = ImageBuffer(buffer_length=4)

    # Set up test conditions
    now = datetime.utcnow()
    test_image = load_image()

    image.send('test', timestamp=now, image=test_image)

    result = get_image_buffer()

    # Verify result
    assert len(result) is 1
    assert result[0] == test_image

@with_setup(teardown=teardown)
def test_return_buffer_length_images():
    buffer_length = 4
    image_buffer_instance = ImageBuffer(buffer_length=buffer_length)

    # Set up test conditions
    now = datetime.utcnow()

    test_images = []
    for i in xrange(0, buffer_length + 1):
        test_image = load_image()
        test_image.tag = "test_image_%d" % i
        test_images.append(test_image)
        image.send('test', timestamp=now + timedelta(seconds=i), image=test_image)

    result = get_image_buffer()

    # Verify result
    assert len(result) is buffer_length

    offset = len(test_images) - buffer_length
    for i in xrange(0, len(result)):
        assert result[i] == test_images[i + offset]