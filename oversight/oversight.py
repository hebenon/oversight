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
import os
import time
import logging
import logging.config

import tensorflow as tf

from im2txt_classifier import Im2TxtClassifier
from image_source import ImageSource
from image_buffer import ImageBuffer
from smtp_notifier import SmtpNotifier
from monitor import Monitor

from logging_config import LOGGING_CONFIG

logger = logging.getLogger('root')


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

    # Create notifiers
    smtp_recipients = args.smtp_recipients.split(',')
    smtp_notifier = SmtpNotifier('Oversight <noreply@oversight.io>', smtp_recipients, args.smtp_host)

    # Parse any triggers, and create monitor
    triggers = parse_triggers(args.triggers)
    logger.info('Triggers: ' + str(triggers))
    monitor = Monitor(triggers)

    # Create classifiers
    logger.info('Loading im2txt classifier...')
    classifier = Im2TxtClassifier(args.model_directory)

    # Create image buffer
    image_buffer = ImageBuffer(args.image_buffer_length)

    # Create image source
    logger.info('Creating image source...')
    image_source = ImageSource(args.download_url, args.download_username, args.download_password)

    while True:
        time.sleep(2)

if __name__ == '__main__':
    logger.info('Initialising Tensorflow...')
    tf.app.run()
