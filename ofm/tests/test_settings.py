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

from ofm.core.settings import Settings
from ofm.defaults import NAMES_FILE


def test_get_settings(settings: Settings):
    expected_data = {
        "res": str(settings.res),
        "images": str(settings.images),
        "db": str(settings.db),
        "save": str(settings.save),
        "clubs_def": str(settings.clubs_def),
        "fifa_codes": str(settings.fifa_codes),
        "fifa_conf": str(settings.fifa_conf),
        "squads": os.path.join(settings.db, "squads.json"),
        "players": os.path.join(settings.db, "players.json"),
        "clubs": os.path.join(settings.db, "clubs.json"),
        "names": NAMES_FILE,
    }
    settings.create_settings()
    settings.load_settings()
    assert settings.get_data() == expected_data
