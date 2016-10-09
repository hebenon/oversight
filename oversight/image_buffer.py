__author__ = 'bcarson'

from signals import image, image_buffer


class ImageBuffer(object):
    def __init__(self, buffer_length=3):
        self.buffer_length = buffer_length
        self.image_buffer = []

        # Handle image events
        image.connect(self.handle_image)
        image_buffer.connect(self.handle_image_buffer)

    def handle_image(self, sender, **data):
        source_image = data['image']

        if source_image is not None:
            self.image_buffer = [source_image] + self.image_buffer[:int(self.buffer_length) - 1]

    def handle_image_buffer(self, sender):
        return self.image_buffer