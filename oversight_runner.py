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
import logging
import logging.config
import time
from urllib.parse import urlparse

import os
import tensorflow as tf

from oversight.cnn_classifier import CNNClassifier
from oversight.object_detector import ObjectDetector
from oversight.image_buffer import ImageBuffer
from oversight.image_source import ImageSource
from oversight.logging_config import LOGGING_CONFIG
from oversight.monitor import Monitor
from oversight.notifiers.pushover_notifier import PushoverNotifier
from oversight.notifiers.smtp_notifier import SmtpNotifier
from oversight.notifiers.image_file_notifier import ImageFileNotifier

logger = logging.getLogger('root')


def validate_args():
    """
    Validate the provided arguments and return a parsed object.
    Because we use os.environ to provide the default value for unprovided arguments,
    we have to manually check for mandatory arguments.

    :return: parsed ArgumentParser object
    """
    parser = argparse.ArgumentParser(description='oversight')
    parser.add_argument('--download_urls', default=os.environ.get('OVERSIGHT_DOWNLOAD_URLS', '').split(' '), nargs='*')
    parser.add_argument('--model_directory', default=os.environ.get('OVERSIGHT_MODEL_DIRECTORY', '~/.oversight'))
    parser.add_argument('--detector_module_handle', default=os.environ.get('OVERSIGHT_DETECTOR_MODULE_HANDLE', 'https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1'))
    parser.add_argument('--image_buffer_length', default=os.environ.get('OVERSIGHT_IMAGE_BUFFER_LENGTH', 3), type=int)
    parser.add_argument('--notification_delay', default=os.environ.get('OVERSIGHT_NOTIFICATION_DELAY', 2), type=int)
    parser.add_argument('--smtp_recipients', default=os.environ.get('OVERSIGHT_SMTP_RECIPIENTS', ''), nargs='*')
    parser.add_argument('--smtp_host', default=os.environ.get('OVERSIGHT_SMTP_HOST', ''))
    parser.add_argument('--pushover_user', default=os.environ.get('OVERSIGHT_PUSHOVER_USER', ''))
    parser.add_argument('--pushover_token', default=os.environ.get('OVERSIGHT_PUSHOVER_TOKEN', ''))
    parser.add_argument('--pushover_device', default=os.environ.get('OVERSIGHT_PUSHOVER_DEVICE', ''))
    parser.add_argument('--image_storage_directory', default=os.environ.get('OVERSIGHT_IMAGE_STORAGE_DIRECTORY'))
    parser.add_argument('--triggers', default=os.environ.get('OVERSIGHT_TRIGGERS', '').split(' '), nargs='*')
    parser.add_argument('--log_level', default=os.environ.get('OVERSIGHT_LOG_LEVEL', 'INFO'))
    args = parser.parse_args()

    # Mandatory args
    if len(args.download_urls) < 1:
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


def create_image_sources(image_args):
    """
    Parses a list of name:url pairs to create a list of image sources.
    :param image_args: list of name:url pairs that describe image sources.
    :return: list of image sources
    """
    image_sources = []
    for image_source in image_args:
        (tag, image_url) = image_source.split(":", 1)
        parsed = urlparse(image_url)

        plain_url = "%s://%s%s%s" % (parsed.scheme,
                                     parsed.hostname,
                                     ":%s" % parsed.port if parsed.port else "", parsed.path)
        ImageSource(plain_url, parsed.username, parsed.password, tag=tag)

    return image_sources


def main():
    args = validate_args()

    # Configure logging
    LOGGING_CONFIG["loggers"]["root"]["level"] = args.log_level
    logging.config.dictConfig(LOGGING_CONFIG)

    # Create notifiers
    notifiers = []
    smtp_recipients = args.smtp_recipients.split(',')
    if len(smtp_recipients) > 0 and args.smtp_host:
        notifiers.append(SmtpNotifier('Oversight <noreply@oversight.tech>', smtp_recipients, args.smtp_host))

    if args.pushover_user and args.pushover_token:
        notifiers.append(PushoverNotifier(args.pushover_user, args.pushover_token))

    if args.image_storage_directory:
        notifiers.append(ImageFileNotifier(args.image_storage_directory))

    # Parse any triggers, and create monitor
    triggers = parse_triggers(args.triggers)
    logger.info('Triggers: ' + str(triggers))
    monitor = Monitor(triggers, args.notification_delay)

    # Create classifiers
    logger.info('Loading classifier...')
    #classifier = CNNClassifier(args.model_directory, sess)
    classifier = ObjectDetector(args.detector_module_handle)

    # Create image buffer
    image_buffer = ImageBuffer(args.image_buffer_length * len(args.download_urls))

    # Create image source
    logger.info('Creating image sources...')
    image_sources = create_image_sources(args.download_urls)

    while True:
        time.sleep(2)

if __name__ == '__main__':
    main()
