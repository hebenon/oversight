__author__ = 'bcarson'

from PIL import Image

def load_image(path='./data/picture.jpeg'):
    return Image.open(path)