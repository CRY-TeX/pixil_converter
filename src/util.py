import re
import numpy as np
from PIL import Image


def read_pixel_data(png_path):
    im = Image.open(png_path)
    pixels = np.array(im.getdata())
    width, height = im.size
    pixels = pixels.reshape(height, width, 4)
    return pixels


def read_p_type_pixel_data(png_path):

    pixels = read_pixel_data(png_path)
    new_pixels = []
    for row in pixels:
        new_pixels.append([])
        for col in row:
            new_pixels[-1].append(list(map(lambda x: x.item(), col)))

    return new_pixels


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


def get_rgba_colors(pixel_rgba):
    return {tuple(col) for row in pixel_rgba for col in row}


def map_colors(pixel_data, color_map: dict):
    block_image_data = []
    for row in pixel_data:
        block_image_data.append('')
        for pixel in row:
            for key, val in color_map.items():
                if tuple(val) == tuple(pixel):
                    block_image_data[-1] += key
                    break

    return block_image_data
