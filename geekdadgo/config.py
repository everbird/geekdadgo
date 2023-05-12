#!/usr/bin/env python3

import os
import tomlkit


class Config(object):

    def __init__(self, name):
        self.name = name
        self.data = None

    @property
    def optional_config_paths(self):
        return [
            '.{name}.conf'.format(name=self.name),
            os.path.expanduser(
                '~/.{name}.conf'.format(name=self.name)
            ),
        ]

    def read(self, config_path=None):
        if config_path:
            with open(config_path) as f:
                self.data = tomlkit.load(f)
                return

        assert len(self.optional_config_paths) > 0, "At least 1 config file required."

        for config_path in self.optional_config_paths:
            if os.path.isfile(config_path):
                with open(config_path) as f:
                    self.data = tomlkit.load(f)
                return


    def get_ocr_config(self, kind):
        ocr = self.data[f"ocr"][kind]
        return f"--oem {ocr['oem']} --psm {ocr['psm']} -c tessedit_char_whitelist={ocr['whitelist']} -c tessedit_char_blacklist={ocr['blacklist']}"

    @property
    def ocr_date_config(self):
        return self.get_ocr_config("date")

    @property
    def ocr_time_config(self):
        return self.get_ocr_config("time")
