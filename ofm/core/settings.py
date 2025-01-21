#      Openfoot Manager - A free and open source soccer management simulation
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
from pathlib import Path
from typing import Union

import yaml

from ofm.defaults import NAMES_FILE, PROJECT_DIR


class Settings:
    def __init__(
        self,
        root_dir: Union[str, Path] = PROJECT_DIR,
        settings: Union[str, Path] = os.path.join(PROJECT_DIR, "settings.yaml"),
    ) -> None:
        self.root_dir = root_dir
        self.res: Path = Path(os.path.join(root_dir, "res"))
        self.images: Path = Path(os.path.join(root_dir, "images"))
        self.db: Path = Path(os.path.join(self.res, "db"))
        self.save: Path = Path(os.path.join(root_dir, "save"))
        self.clubs_def: Path = Path(os.path.join(self.res, "clubs_def.json"))
        self.fifa_codes: Path = Path(os.path.join(self.res, "fifa_country_codes.json"))
        self.fifa_conf: Path = Path(os.path.join(self.res, "fifa_confederations.json"))
        self.squads_file: Path = Path(os.path.join(self.db, "squads.json"))
        self.players_file: Path = Path(os.path.join(self.db, "players.json"))
        self.clubs_file: Path = Path(os.path.join(self.db, "clubs.json"))
        self.names_file: Path = Path(NAMES_FILE)
        self.settings_file: Path = Path(settings)

    def get_data(self) -> dict:
        return {
            "res": str(self.res),
            "images": str(self.images),
            "db": str(self.db),
            "save": str(self.save),
            "clubs_def": str(self.clubs_def),
            "fifa_codes": str(self.fifa_codes),
            "fifa_conf": str(self.fifa_conf),
            "squads": str(self.squads_file),
            "players": str(self.players_file),
            "clubs": str(self.clubs_file),
            "names": str(self.names_file),
        }

    def parse_settings(self, data: dict) -> None:
        default_settings = self.get_data()
        try:
            self.res = Path(data["res"])
            self.images = Path(data["images"])
            self.db = Path(data["db"])
            self.save = Path(data["save"])
            self.clubs_def = Path(data["clubs_def"])
            self.fifa_codes = Path(data["fifa_codes"])
            self.fifa_conf = Path(data["fifa_conf"])
            self.squads_file = Path(data["squads"])
            self.players_file = Path(data["players"])
            self.clubs_file = Path(data["clubs"])
            self.names_file = Path(data["names"])
        except KeyError:
            self.parse_settings(default_settings)

    def load_settings(self) -> None:
        with open(self.settings_file, "r") as fp:
            data = yaml.safe_load(fp)
            self.parse_settings(data)

    def create_settings(self) -> None:
        with open(self.settings_file, "w") as fp:
            yaml.safe_dump(self.get_data(), fp)

    def get_settings(self) -> None:
        if os.path.exists(self.settings_file):
            self.load_settings()
        else:
            self.create_settings()
