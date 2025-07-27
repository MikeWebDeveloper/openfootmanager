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
from copy import deepcopy
from typing import Callable

from ttkbootstrap import Toplevel

from ...core.football.formation import FORMATION_STRINGS
from ...core.football.team_simulation import PlayerSimulation, TeamSimulation
from ...core.simulation.live_game_manager import LiveGameManager
from ..pages.debug_match.substitution_window import SubstitutionWindow


class SubstitutionWindowController:
    def __init__(
        self,
        parent: Toplevel,
        team: TeamSimulation,
        live_game_manager: LiveGameManager,
        start_match: Callable,
    ):
        self.page = SubstitutionWindow(parent)
        self.original_team = team
        self.team = deepcopy(team)
        self.live_game_manager = live_game_manager
        self.start_match = start_match
        self.initialize()
        self._bind()

    @property
    def live_game(self):
        return self.live_game_manager.live_game

    @live_game.setter
    def live_game(self, value):
        self.live_game_manager.live_game = value

    def initialize(self):
        self.live_game.running = False
        self.page.update_team_name(self.team.club.name)
        self.update_formation_table()
        self.update_reserves_table()
        self.page.update_formations(FORMATION_STRINGS)
        self.page.update_formation_box(self.team.formation.formation_string)
        self.get_substitution_amount()

    def get_substitution_amount(self):
        subs = (
            self.team.max_substitutions
            - self.team.substitutions
            - self.team.temporary_subs
        )
        self.page.update_substitution_amount(subs)

    def get_player_data(self, players: list[PlayerSimulation]) -> list[tuple]:
        return [
            (
                player.player.details.short_name.encode("utf-8").decode(
                    "unicode_escape"
                ),
                player.current_position.name.encode("utf-8").decode("unicode_escape"),
                player.stamina,
                "Yes" if player.is_injured else "No",
                player.current_skill,
            )
            for player in players
        ]

    def update_team_formation(self, *args):
        self.update_formation_table()

    def update_formation_table(self):
        player_data = self.get_player_data(self.team.formation.players)
        self.page.update_team_table(player_data)

    def update_reserves_table(self):
        player_data = self.get_player_data(self.team.formation.bench)
        self.page.update_reserves_table(player_data)

    def apply_changes(self):
        if self.original_team == self.live_game.engine.home_team:
            self.live_game.engine.home_team = self.team
        else:
            self.live_game.engine.away_team = self.team

        self.return_game()

    def return_game(self):
        if not self.live_game.is_game_over:
            self.live_game.running = True

        self.start_match()
        self.page.destroy()

    def cancel(self):
        result = self.page.cancel_dialog()

        if result == self.page.get_yes_result():
            self.return_game()

    def get_player_from_table(self, player_data: list) -> PlayerSimulation:
        for player in self.team.formation.players:
            pl = [
                player.player.details.short_name.encode("utf-8").decode(
                    "unicode_escape"
                ),
                player.current_position.name.encode("utf-8").decode("unicode_escape"),
                str(player.stamina),
                "Yes" if player.is_injured else "No",
                player.current_skill,
            ]
            if pl == player_data:
                return player

    def get_player_from_reserves_table(self, player_data: list) -> PlayerSimulation:
        for player in self.team.formation.bench:
            pl = [
                player.player.details.short_name.encode("utf-8").decode(
                    "unicode_escape"
                ),
                player.current_position.name.encode("utf-8").decode("unicode_escape"),
                str(player.stamina),
                "Yes" if player.is_injured else "No",
                player.current_skill,
            ]
            if pl == player_data:
                return player

    def sub_player(self):
        player_out = self.page.substitution_tab.team_table.item(
            self.page.substitution_tab.team_table.focus()
        )["values"]
        player_in = self.page.substitution_tab.reserves_table.item(
            self.page.substitution_tab.reserves_table.focus()
        )["values"]
        player_out = self.get_player_from_table(player_out)
        player_in = self.get_player_from_reserves_table(player_in)

        if player_out and player_in:
            self.update_formation_table()
            self.update_reserves_table()
            self.get_substitution_amount()

    def _bind(self):
        self.page.cancel_button.config(command=self.cancel)
        self.page.apply_button.config(command=self.apply_changes)
        self.page.substitution_tab.formation_combobox.bind(
            "<<ComboboxSelected>>", self.update_team_formation
        )
        self.page.substitution_tab.button_in.config(command=self.sub_player)
        self.page.substitution_tab.button_out.config(command=self.sub_player)
        self.page.protocol("WM_DELETE_WINDOW", self.cancel)
