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
    start_empty_line = 0
    end_content_line = -1

    for i, line in enumerate(block_image_data):
        if re.search('^\s*$', line):
            start_empty_line = i
        else:
            break

    for i, line in enumerate(reversed(block_image_data)):
        if re.search('^\s*$', line):
            end_content_line = -i
        else:
            break

    return block_image_data[start_empty_line:end_content_line]


def remove_empty_columns(block_image_data):
    remove_start = 1000000
    remove_end = 0
    for line in block_image_data:
        match_start = re.search('^\s*\w', line)
        if match_start:
            if remove_start > match_start.span()[1]-1:
                remove_start = match_start.span()[1]-1

        match_end = re.search('\w\s*$', line)
        if match_end:
            if remove_end < match_end.span()[0]+1:
                remove_end = match_end.span()[0]+1

    return [line[remove_start:remove_end] for line in block_image_data]


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
    block_image_data = remove_empty_columns(block_image_data)

    with open(output_path, 'w') as wf:
        wf.write('\n'.join(block_image_data))


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(f'Exceution finished. Duration: {end-start:.3f}s')
