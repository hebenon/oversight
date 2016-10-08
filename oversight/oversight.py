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

import argparse
import io
import os
import time
import logging
import logging.config

import tensorflow as tf

from PIL import Image

from cnnclassifier import CNNClassifier
from image_source import ImageSource
from smtp_notifier import SmtpNotifier

from logging_config import LOGGING_CONFIG

logger = logging.getLogger('root')

# Size of images to work with
output_width = 1000
output_height = 565


def validate_args():
    """
    Validate the provided arguments and return a parsed object.
    Because we use os.environ to provide the default value for unprovided arguments,
    we have to manually check for mandatory arguments.

    :return: parsed ArgumentParser object
    """
    parser = argparse.ArgumentParser(description='oversight')
    parser.add_argument('--download_url', default=os.environ.get('OVERSIGHT_DOWNLOAD_URL', None))
    parser.add_argument('--download_username', default=os.environ.get('OVERSIGHT_DOWNLOAD_USERNAME', None))
    parser.add_argument('--download_password', default=os.environ.get('OVERSIGHT_DOWNLOAD_PASSWORD', None))
    parser.add_argument('--model_directory', default=os.environ.get('OVERSIGHT_MODEL_DIRECTORY', '~/.oversight'))
    parser.add_argument('--image_buffer_length', default=os.environ.get('OVERSIGHT_IMAGE_BUFFER_LENGTH', 3), type=int)
    parser.add_argument('--smtp_recipients', default=os.environ.get('OVERSIGHT_SMTP_RECIPIENTS', ''), nargs='*')
    parser.add_argument('--smtp_host', default=os.environ.get('OVERSIGHT_SMTP_HOST', ''))
    parser.add_argument('--triggers', default=os.environ.get('OVERSIGHT_TRIGGERS', '').split(' '), nargs='*')
    parser.add_argument('--log_level', default=os.environ.get('OVERSIGHT_LOG_LEVEL', 'INFO'))
    args = parser.parse_args()

    # Mandatory args
    if not args.download_url:
        exit(parser.print_usage())

    return args


def get_resized_image(image_input):
    """
    Given a raw image from an image source, resize it to a standard size. Doing this results in more consistent
    results against the training set.

    :param image_input: A buffer with the raw image data.
    :return: Resized image data in jpeg format.
    """
    image = Image.open(image_input)
    resized_image = image.resize((output_width, output_height))

    output_buffer = io.BytesIO()
    resized_image.save(output_buffer, 'jpeg')

    return output_buffer.getvalue()


def parse_triggers(trigger_args):
    """
    Parses a list of trigger:threshold pairs to return a dictionary of triggers.
    I've used a function instead of a list slice for the opportunity to apply validation.

    :param trigger_args: List of trigger:threshold pairs.
    :return: Dictionary of trigger -> threshold.
    """
    triggers = {}

    for trigger_pair in trigger_args:
        (trigger, threshold) = trigger_pair.split(':')
        triggers[trigger] = float(threshold)

    return triggers


def main(_):
    args = validate_args()

    # Configure logging
    LOGGING_CONFIG["loggers"]["root"]["level"] = args.log_level
    logging.config.dictConfig(LOGGING_CONFIG)

    smtp_recipients = args.smtp_recipients.split(',')
    image_buffer = []

    # Parse any triggers.
    triggers = parse_triggers(args.triggers)
    active_triggers = set()
    logger.info('Triggers: ' + str(triggers))

    logger.info('Loading classifier...')
    classifier = CNNClassifier(args.model_directory)

    logger.info('Creating image source...')
    image_source = ImageSource(args.download_url, args.download_username, args.download_password)
    smtp_notifier = SmtpNotifier('Oversight <noreply@oversight.io>', args.smtp_host)

    with tf.Session() as session:

        while True:
            # Get image and add to the buffer.
            source_image = image_source.get_image()

            if source_image is not None:
                image = get_resized_image(source_image)
                image_buffer = [image] + image_buffer[:int(args.image_buffer_length) - 1]

                # Get predictions
                predictions = classifier.predict(session, image)

                # Check for a result
                for (prediction, probability) in predictions:
                    logger.debug("prediction %s: %f", prediction, probability)

                    # The graph uses softmax in the final layer, so it's *unlikely* that this will be useful.
                    # That being said, it's possible to configure multiple triggers with low thresholds.
                    if prediction in triggers and probability >= triggers[prediction]:
                        # Prevent alarm storms by not acting on active triggers
                        if prediction not in active_triggers:
                            logger.warning("Trigger event active: %s %f", prediction, probability)
                            active_triggers.add(prediction)
                            smtp_notifier.send_notification(prediction, image_buffer, smtp_recipients)
                    else:
                        # Log any clearing alarms
                        if prediction in active_triggers:
                            logger.warning("Trigger event ended: %s %f", prediction, probability)

                        active_triggers.discard(prediction)  # Remove from active triggers (if it exists)

            time.sleep(2)

if __name__ == '__main__':
    logger.info('Initialising Tensorflow...')
    tf.app.run()
