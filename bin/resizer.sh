#!/usr/bin/python

__author__ = 'bcarson'
# Simple script to resize raw images into standard format.

import sys
import os
import argparse

from PIL import Image

parser = argparse.ArgumentParser(description='resizer')
parser.add_argument('--input_path', default='./labelled_images_raw')
parser.add_argument('--output_path', default='./labelled_images')
parser.add_argument('--output_width', default='1000')
parser.add_argument('--output_height', default='565')

if __name__ == "__main__":
    args = parser.parse_args()

    output_width = int(args.output_width)
    output_height = int(args.output_height)

    input_path = args.input_path
    output_path = args.output_path

    for category in [path for path in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, path))]:
        output_category_path = os.path.join(output_path, category)
        input_category_path = os.path.join(input_path, category)

        if not os.path.exists(output_category_path):
            os.mkdir(output_category_path)

        for image_file in os.listdir(input_category_path):
            output_file_path = os.path.join(output_category_path, image_file)
            input_file_path = os.path.join(input_category_path, image_file)

            im = Image.open(input_file_path)
            im.resize((output_width, output_height)).save(output_file_path)