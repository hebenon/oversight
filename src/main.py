__author__ = 'bcarson'

import argparse
import io
import os
import time

import tensorflow as tf

from PIL import Image

from oversight.classifier import Classifier
from oversight.imagesource import ImageSource
from oversight.smtp_notifier import SmtpNotifier


# Size of images to work with
output_width = 1000
output_height = 565

# Trigger certainty levels
triggers = {
    #"nothing": 0.1,
    "person": 0.85,
    "car": 0.85
}


def validate_args():
    parser = argparse.ArgumentParser(description='oversight')
    parser.add_argument('--download_url', default=os.environ.get('OVERSIGHT_DOWNLOAD_URL', None))
    parser.add_argument('--download_username', default=os.environ.get('OVERSIGHT_DOWNLOAD_USERNAME', None))
    parser.add_argument('--download_password', default=os.environ.get('OVERSIGHT_DOWNLOAD_PASSWORD', None))
    parser.add_argument('--model_directory', default=os.environ.get('OVERSIGHT_MODEL_DIRECTORY', None))
    parser.add_argument('--image_buffer_length', default=os.environ.get('OVERSIGHT_IMAGE_BUFFER_LENGTH', None))
    parser.add_argument('--smtp_recipients', default=os.environ.get('OVERSIGHT_SMTP_RECIPIENTS', None))
    args = parser.parse_args()

    # Mandatory args
    if not args.download_password:
        exit(parser.print_usage())

    # Args with defaults
    if not args.image_buffer_length:
        args.image_buffer_length = 3

    if not args.model_directory:
        args.model_directory = "~/.oversight"

    return args


def get_image(image_input):
    image = Image.open(image_input)
    resized_image = image.resize((output_width, output_height))

    output_buffer = io.BytesIO()
    resized_image.save(output_buffer, "jpeg")

    return output_buffer.getvalue()


def main(_):
    args = validate_args()

    smtp_recipients = args.smtp_recipients.split(",")
    image_buffer = []

    print("Loading classifier...")
    classifier = Classifier(args.model_directory)

    print("Creating image source...")
    image_source = ImageSource(args.download_url, args.download_username, args.download_password)
    smtp_notifier = SmtpNotifier("Oversight <noreply@oversight.io>", "smtp.bigpond.com")

    with tf.Session() as session:

        while True:
            # Get image and add to the buffer.
            source_image = image_source.get_image()

            if source_image is not None:
                image = get_image(source_image)
                image_buffer = [image] + image_buffer[:int(args.image_buffer_length) - 1]

                # Get predictions
                predictions = classifier.predict(session, image)

                # Check for a result
                for result in predictions:
                    print("%s: %f" % result)
                print("")

                head_prediction = predictions[0]
                if head_prediction[0] in triggers and head_prediction[1] >= triggers[head_prediction[0]]:
                    smtp_notifier.send_notification(head_prediction[0], image_buffer, smtp_recipients)

            time.sleep(2)

if __name__ == "__main__":
    print("Initialising Tensorflow...")
    tf.app.run()
