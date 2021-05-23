import os
import time
import json
import re
import numpy as np

import util


def pick_color(pixel_rgba, color_mapping) -> str:
    pick = " "
    offset = 1000000
    for key, value in color_mapping.items():
        curr_offset = sum([abs(pixel_rgba[i]-value[i]) for i in range(4)])
        if curr_offset < offset:
            offset = curr_offset
            pick = key
    return pick


def remove_empty_lines(block_image_data):
    return [el for el in block_image_data if re.search('[a-zA-z]', el)]


def main():
    # read config
    config = json.load(
        open(os.path.join(os.path.dirname(__file__), '../config/config.json'), 'r'))

    image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              config['asset_folder_path'], config['image_name'])

    output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               config['output_path'], f'{os.path.splitext(config["image_name"])[0]}.txt')

    color_mapping = config['color_mapping']

    pixels = util.read_pixel_data(image_path)

    block_image_data = []
    for row in pixels:
        block_image_data.append(
            ''.join([pick_color(el, color_mapping) for el in row]))

    block_image_data = remove_empty_lines(block_image_data)

    with open(output_path, 'w') as wf:
        wf.write('\n'.join(block_image_data))


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(f'Exceution finished. Duration: {end-start:.3f}s')
