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
import json
import uuid
from unittest.mock import Mock

import pytest

from ofm.core.db.database import DB, DatabaseLoadError, PlayerTeamLoadError
from ofm.core.db.generators import PlayerGenerator
from ofm.core.settings import Settings


@pytest.fixture
def db(settings, confederations_file) -> DB:
    fifa_conf = settings.res / "fifa_confederations.json"
    with fifa_conf.open("w") as fp:
        json.dump(confederations_file, fp)

    return DB(settings)


def test_generate_players(db: DB):
    expected_players = db.generate_players()
    file_contents = db.load_players()
    assert file_contents is not None
    assert expected_players == file_contents


def test_get_non_existent_player_from_database(db: DB):
    with pytest.raises(DatabaseLoadError):
        db.get_player_object_from_id(uuid.uuid4(), [{"id": uuid.uuid4().int}])


def test_get_player_from_empty_players_list(db: DB):
    with pytest.raises(DatabaseLoadError):
        db.get_player_object_from_id(uuid.uuid4(), [])


def test_get_player_from_player_list(db: DB):
    player = PlayerGenerator(db.settings).generate_player()
    player_dict = player.serialize()
    pl_id = player.player_id
    assert db.get_player_object_from_id(pl_id, [player_dict]) == player


def test_load_player_from_dict(db: DB):
    player = PlayerGenerator(db.settings).generate_player()
    player_dict = player.serialize()
    assert db.load_player_objects([player_dict]) == [player]


def test_raises_database_load_error_get_player_team_from_dict(db: DB):
    players = [Mock(player_id=uuid.uuid4())]
    squad_ids = [{"player_id": uuid.uuid4().int}]
    with pytest.raises(PlayerTeamLoadError):
        db.get_player_team_from_dicts(squad_ids, players)


def test_raises_error_get_player_team_from_dict(db: DB):
    players = []
    squad_ids = [{"id": uuid.uuid4().int}]
    with pytest.raises(PlayerTeamLoadError):
        db.get_player_team_from_dicts(squad_ids, players)


def test_generate_and_load_clubs_and_players(db: DB, squads_def):
    db.generate_teams_and_squads(squads_def)
    clubs_dict = db.load_clubs()
    players_dict = db.load_players()
    players_obj = db.load_player_objects(players_dict)
    clubs_obj = db.load_club_objects(clubs_dict, players_dict)
    assert [club.serialize() for club in clubs_obj] == clubs_dict
    assert [player.serialize() for player in players_obj] == players_dict
