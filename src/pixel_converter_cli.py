import sys
import os
import getopt
import json
import codecs
import shutil

import util

help_str = """
    usage: <png_file> [ <output_path> ]

    reset: reset config

    -f: filename of the file to convert
    -o: output path -> OPTIONAL
"""

arg_list = [('filename', 'f'), ('output_path', 'o')]
config_path = os.path.join(os.path.dirname(__file__), '../config/cli_config.json')
reset_config_path = os.path.join(os.path.dirname(__file__), '../config/cli_config_backup.json')


def parse_cli_args() -> dict:

    data_dict = {}
    opts, args = getopt.getopt(sys.argv[1:], f"{':'.join([abbrev for name, abbrev in arg_list])}:", [name for name, abbrev in arg_list])

    # print("opts:", opts)
    # print("args:", args)

    if len(opts) + len(args) > 2:
        return None

    for descriptor, value in opts:
        for name, abbrev in arg_list:
            if abbrev == descriptor.replace('-', ''):
                data_dict[name] = value
                break

    for el in args:
        data_dict[arg_list[len(data_dict)][0]] = el

    return data_dict


def args_valid(args: dict) -> bool:

    if args == None:
        print("Invalid arguments")
        print(help_str)
        return False

    if not "filename" in args.keys():
        print("input path missing")
        return False

    input_file = args.get('filename')
    if not os.path.exists(input_file) or not os.path.isfile(input_file):
        print(f'"{input_file}" is not a valid input file')
        return False

    if not os.path.splitext(input_file)[1] == ".png":
        print(f'"{input_file}" needs to have the .png format')
        return False

    if not "output_path" in args.keys():
        output_path = os.path.abspath('.')
    else:
        output_path = args.get('output_path')

    if not os.path.exists(output_path) or not os.path.isdir(output_path):
        print(f'"{output_path}" is not a valid output path')
        return False

    return True


def get_missing_colors(color_map: dict, picture_colors: set) -> set:
    color_map_set = {tuple(val) for key, val in color_map.items()}
    return picture_colors - color_map_set


def map_missing_colors(missing_colors: set, color_map: dict, char_pos: int, reserved_letters: list):
    new_color_map = color_map.copy()
    for col in missing_colors:

        mapping_letter = chr(ord('@')+char_pos)
        while mapping_letter in reserved_letters:
            char_pos += 1
            mapping_letter = chr(ord('@')+char_pos)

        new_color_map[mapping_letter] = col
        char_pos += 1

    return new_color_map, char_pos


def main():

    # handle reset
    # jenky but im exhausted
    if len(sys.argv) == 2:
        if sys.argv[1] == 'reset':
            if not os.path.isfile(config_path) or not os.path.isfile(reset_config_path):
                print('unable to reset cause config or backup file could not be found')
                return

            shutil.copyfile(reset_config_path, config_path)
            print('Successfully reset config')
            return

    # parse command line arguments
    #   -> check arguments for validity
    # valid arguments:
    #   -> required: filename to png
    #   -> optional: output path
    args = parse_cli_args()

    if not args_valid(args):
        return

    image_path = args.get('filename')
    output_path = args.get('output_path', os.path.abspath('.'))
    # image_path = 'assets/fighter_jet.png'
    # output_path = '.'

    # read config -> cli config
    #   -> read in color mappings
    #   -> read stopping unicode char for colors
    if not os.path.exists(config_path):
        print(f'No configuration file could be found at path "{config_path}"')
        return

    config = None
    with open(config_path) as config_file:
        config = json.load(config_file)

    if config is None:
        print('Configuration could not be read')
        return

    # read in picture file
    pixel_data = util.read_p_type_pixel_data(image_path)

    # TODO: automatic resize would be nice

    # TODO: color reduction -> average out colors

    # extract all new colors out of picture
    colors = util.get_rgba_colors(pixel_data)

    color_map = config.get('color_map').get('added')
    missing_colors = get_missing_colors(color_map, colors)

    # map missing colors
    if len(missing_colors) != 0:
        # FIXME: could also check color map in case letter_position is wrong
        color_map, config['letter_position'] = map_missing_colors(
            missing_colors, color_map, config.get('letter_position'), config.get('color_map').get('reserved'))

        # add the new config values to config file
        config['color_map']['added'] = color_map
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file)

    # convert to block image file with all colors mapped to the actual color
    block_image_data = util.map_colors(pixel_data, color_map)
    block_image_data = util.remove_empty_lines(block_image_data)
    block_image_data = util.remove_empty_columns(block_image_data)

    # output section
    output_block_file_prefix = os.path.splitext(os.path.basename(image_path))[0]

    # output block image file
    block_image_file_path = os.path.join(output_path, f'{output_block_file_prefix}.txt')
    with codecs.open(block_image_file_path, 'w', encoding='utf-8') as output_block_file:
        output_block_file.write('\n'.join(block_image_data))

    # output color map
    color_map_file_path = os.path.join(output_path, f'{output_block_file_prefix}_colormap.json')
    with open(color_map_file_path, 'w') as color_map_file:
        json.dump(color_map, color_map_file)

    # print info messages
    print(f'Successfully converted "{image_path}"')
    print(f'Output block image: "{block_image_file_path}"')
    print(f'Output color map: "{color_map_file_path}"')


if __name__ == '__main__':
    main()
