__author__ = 'bcarson'

import io
from PIL import Image

def load_image(path='./data/picture.jpeg', output_width=1000, output_height=565):
    image = Image.open(path)
    resized_image = image.resize((output_width, output_height))

    output_buffer = io.BytesIO()
    resized_image.save(output_buffer, 'jpeg')

    return output_buffer.getvalue()