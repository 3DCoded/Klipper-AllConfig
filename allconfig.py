# AllConfig
#
# Utility for Klipper firmware to allow outputting the entire
# config to a file, as Klipper sees it.
# This can help debug cases where one section overrides another,
# Or with include statements.
#
# Copyright (C) 2025 Christopher Mattar (3dcoded)
#                    <info3dcoded@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#

import textwrap
from pathlib import Path

INDENT = ' '*4
HEADER = """
# This file contains the config that Klipper actually sees.
# Note that this may be different that what is in your printer.cfg
# because there may be multiple sections overriding each other.
#
# Example:
# # In one file
# [extruder]
# step_pin: xxx
# dir_pin: xxx
# en_pin: !xxx
# rotation_distance: 40
# ...
#
# # In another file included into printer.cfg
# [extruder]
# rotation_distance: 32
#
# Klipper only sees what happens last, so if the config was loaded
# in the order shown in the previous example, Klipper would see:
#
# [extruder]
# step_pin: xxx
# dir_pin: xxx
# en_pin: !xxx
# rotation_distance: 32 # <-- NOTE the different rotation_distance
#
# This also takes into account SAVE_CONFIG.
# Example:
#
# #*# <---------------------- SAVE_CONFIG ---------------------->
# #*# DO NOT EDIT THIS BLOCK OR BELOW. The contents are auto-generated.
# #*#
# #*# [extruder]
# #*# pid_kp: 21.432
# #*# pid_ki: 1.856
# #*# pid_kd: 61.884
#
# In this example, including the previous [extruder] section,
# Klipper would see:
#
# [extruder]
# step_pin: xxx
# dir_pin: xxx
# en_pin: !xxx
# rotation_distance: 32
# pid_kp: 21.432
# pid_ki: 1.856
# pid_kd: 61.884

"""

class PrinterAllConfig:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config

        cfg_folder = Path(self.printer.start_args['config_file']).parent
        self.output_path = Path(config.get('output', str(cfg_folder / 'allconfig.cfg')))

        self.printer.register_event_handler('klippy:connect', self.handle_connect)

    def handle_connect(self):
        allconfig = ''+HEADER
        for section in self.config.fileconfig.sections():
            allconfig += f'[{section}]\n'
            for option, value in self.config.fileconfig.items(section):
                if len(value.splitlines()) == 1:
                    allconfig += f'{option}: {value}\n'
                else:
                    updated_value = textwrap.indent(value.strip(), INDENT)
                    allconfig += f'{option}:\n{updated_value}\n'
            allconfig += '\n'

        with open(self.output_path, 'w+') as file:
            file.write(allconfig)

def load_config(config):
    return PrinterAllConfig(config)
