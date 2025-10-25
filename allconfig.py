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
import configparser
from io import StringIO
import glob
import os
import logging

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

class ConfigParser:
    def __init__(self, printer):
        global config_path
        self.printer = printer

        self.config_file = printer.start_args['config_file']
        self.config_path = Path(os.path.dirname(self.config_file))
        config_path = self.config_path

    def read_config(self):
        section_filenames = self._read_file(self.config_file)
        return section_filenames

    def _read_file(self, filename, visited=[], section_filenames={}):
        path = self.config_path / filename
        visited.append(path) # Keep a list of files previously included
        with open(path, 'r') as file:
            parser = configparser.RawConfigParser(
            strict=False, inline_comment_prefixes=(';', '#'))
            parser.read_file(file, filename)
            for section in parser.sections():
                if section in section_filenames:
                    section_filenames[section].append(filename)
                else:
                    section_filenames[section] = [filename]

            file.seek(0)

            for line in file.readlines():
                mo = configparser.RawConfigParser.SECTCRE.match(line)
                header = mo and mo.group('header')
                # Handle [include xxx.cfg] sections
                if header and header.startswith('include '):
                    include_spec = header[8:].strip()
                    include_path = str(path.parent / include_spec)
                    include_filenames = glob.glob(include_path, recursive=True)
                    for include_filename in include_filenames:
                        self._read_file(include_filename, visited, section_filenames)

        visited.remove(path)

        return section_filenames

class PrinterAllConfig:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config

        self.cfg_folder = Path(self.printer.start_args['config_file']).parent
        self.output_path = Path(config.get('output', str(self.cfg_folder / 'allconfig.cfg')))

        self.cfg_files = []
        self.section_sources = {}

        self.printer.register_event_handler('klippy:connect', self.handle_connect)

    def handle_connect(self):
        section_filenames = ConfigParser(self.printer).read_config()
        cfg_root = str(self.cfg_folder) + '/'
        for section, files in section_filenames.items():
            section_filenames[section] = [
                f[len(cfg_root):] if f.startswith(cfg_root) else f
                for f in files
    ]

        allconfig = ''+HEADER
        for section in self.config.fileconfig.sections():
            allconfig += f'[{section}]'
            if section in section_filenames:
                sources = section_filenames[section]
                source_str = ', '.join(sources)
                allconfig += f'  # {source_str}'
            allconfig += '\n'

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
