import numpy as np
from PIL import Image


def read_pixel_data(png_path):
    im = Image.open(png_path)
    pixels = np.array(im.getdata())
    width, height = im.size
    pixels = pixels.reshape(height, width, 4)
    return pixels
