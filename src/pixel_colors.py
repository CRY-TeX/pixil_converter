import os
import time
import json
import re
import numpy as np
from PIL import Image

import util


def main():
    # read config
    config = json.load(
        open(os.path.join(os.path.dirname(__file__), '../config/config.json'), 'r'))

    image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              config['asset_folder_path'], config['image_name'])

    output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               config['output_path'], f'colors_{os.path.splitext(config["image_name"])[0]}.txt')

    pixels = util.read_pixel_data(image_path)

    colors = util.get_rgba_colors(pixels)

    with open(output_path, 'w') as wf:
        for color in colors:
            wf.write('[{}]\n'.format(', '.join(map(str, color))))


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(f'Exceution finished. Duration: {end-start:.3f}s')
