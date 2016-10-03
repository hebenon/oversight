__author__ = 'bcarson'

import argparse
import io
import os
import time

import tensorflow as tf

from PIL import Image

from classifier import Classifier
from image_source import ImageSource
from smtp_notifier import SmtpNotifier


# Size of images to work with
output_width = 1000
output_height = 565


def validate_args():
    parser = argparse.ArgumentParser(description='oversight')
    parser.add_argument('--download_url', default=os.environ.get('OVERSIGHT_DOWNLOAD_URL', None))
    parser.add_argument('--download_username', default=os.environ.get('OVERSIGHT_DOWNLOAD_USERNAME', None))
    parser.add_argument('--download_password', default=os.environ.get('OVERSIGHT_DOWNLOAD_PASSWORD', None))
    parser.add_argument('--model_directory', default=os.environ.get('OVERSIGHT_MODEL_DIRECTORY', '~/.oversight'))
    parser.add_argument('--image_buffer_length', default=os.environ.get('OVERSIGHT_IMAGE_BUFFER_LENGTH', 3), type=int)
    parser.add_argument('--smtp_recipients', default=os.environ.get('OVERSIGHT_SMTP_RECIPIENTS', ''), nargs='*')
    parser.add_argument('--smtp_host', default=os.environ.get('OVERSIGHT_SMTP_HOST', ''))
    parser.add_argument('--triggers', default=os.environ.get('OVERSIGHT_TRIGGERS', '').split(' '), nargs='*')
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

    smtp_recipients = args.smtp_recipients.split(',')
    image_buffer = []

    # Parse any triggers.
    triggers = parse_triggers(args.triggers)
    active_triggers = set()
    print('Triggers: ' + str(triggers))

    print('Loading classifier...')
    classifier = Classifier(args.model_directory)

    print('Creating image source...')
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
                    print('%s: %f' % (prediction, probability))

                    # The graph uses softmax in the final layer, so it's *unlikely* that this will be useful.
                    # That being said, it's possible to configure triggers with low thresholds.
                    if prediction in triggers and probability >= triggers[prediction]\
                            and prediction not in active_triggers:
                        active_triggers.add(prediction)
                        smtp_notifier.send_notification(prediction, image_buffer, smtp_recipients)
                    else:
                        active_triggers.discard(prediction)  # Remove from active triggers (if it exists)

                print('')

            time.sleep(2)

if __name__ == '__main__':
    print('Initialising Tensorflow...')
    tf.app.run()
