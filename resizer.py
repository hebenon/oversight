__author__ = 'bcarson'

# Simple script to resize raw images into standard format.

import sys
import os

from PIL import Image

output_width = 1000
output_height = 565

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]

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