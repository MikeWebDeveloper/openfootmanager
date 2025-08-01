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
import random
from dataclasses import dataclass
from typing import Optional

from ...football.player import PlayerSimulation
from ...football.team_simulation import TeamSimulation
from .. import OFF_POSITIONS, PitchPosition
from ..event import CommentaryImportance, EventOutcome, SimulationEvent
from ..event_type import EventType
from ..game_state import GameState
from ..team_strategy import team_pass_strategy


@dataclass
class PassEvent(SimulationEvent):
    commentary_importance = CommentaryImportance.LOW
    receiving_player: Optional[PlayerSimulation] = None

    def get_end_position(self, attacking_team) -> PitchPosition:
        if self.event_type == EventType.CORNER_KICK:
            return self.state.position

        team_strategy = attacking_team.team_strategy
        transition_matrix = team_pass_strategy(team_strategy)
        probabilities = transition_matrix[self.state.position]
        return random.choices(list(PitchPosition), probabilities)[0]

    def get_pass_primary_outcome(self, distance: int) -> EventOutcome:
        outcomes = [
            EventOutcome.PASS_MISS,
            EventOutcome.PASS_SUCCESS,
        ]

        if self.event_type == EventType.FREE_KICK:
            pass_miss = (50 + distance) / (
                100
                + self.attacking_player.attributes.intelligence.passing
                + self.attacking_player.attributes.intelligence.vision
                + self.attacking_player.attributes.offensive.free_kick
            )
        else:
            pass_miss = (25 + distance) / (
                100
                + self.attacking_player.attributes.intelligence.passing
                + self.attacking_player.attributes.intelligence.vision
            )

        pass_success = 1 - pass_miss

        outcome_probability = [
            pass_miss,  # PASS_MISS
            pass_success,  # PASS_SUCCESS
        ]

        return random.choices(outcomes, outcome_probability)[0]

    def get_intercept_prob(self) -> EventOutcome:
        outcomes = [EventOutcome.PASS_MISS, EventOutcome.PASS_INTERCEPT]
        pass_intercept = (
            self.defending_player.attributes.defensive.positioning
            + self.defending_player.attributes.defensive.interception
        )
        outcome_probability = [
            200 - pass_intercept,
            pass_intercept,
        ]

        return random.choices(outcomes, outcome_probability)[0]

    def get_secondary_outcome(self) -> EventOutcome:
        outcomes = [EventOutcome.PASS_SUCCESS, EventOutcome.PASS_OFFSIDE]

        offside_probability = 5 / (
            200
            + self.attacking_player.attributes.offensive.positioning
            + self.attacking_player.attributes.intelligence.team_work
        )

        outcome_probability = [
            1 - offside_probability,
            offside_probability,
        ]
        return random.choices(outcomes, outcome_probability)[0]

    def calculate_event(
        self,
        attacking_team: TeamSimulation,
        defending_team: TeamSimulation,
    ) -> GameState:
        # Transition matrix for each position on the field
        end_position = self.get_end_position(attacking_team)
        distance = abs(
            end_position.value - self.state.position.value
        )  # distance from current position to end position

        if self.attacking_player is None:
            self.attacking_player = attacking_team.player_in_possession
        if self.defending_player is None:
            self.defending_player = defending_team.get_player_on_pitch(end_position)
        self.receiving_player = attacking_team.get_player_on_pitch(end_position)
        self.attacking_player.statistics.passes += 1

        self.outcome = self.get_pass_primary_outcome(distance)

        if self.outcome == EventOutcome.PASS_MISS:
            self.outcome = self.get_intercept_prob()

        if (
            end_position in OFF_POSITIONS
            and self.state.position.value < end_position.value
            and self.outcome == EventOutcome.PASS_SUCCESS
            and self.event_type != EventType.CORNER_KICK
        ):
            self.outcome = self.get_secondary_outcome()

        if self.outcome in [
            EventOutcome.PASS_MISS,
            EventOutcome.PASS_INTERCEPT,
            EventOutcome.PASS_OFFSIDE,
        ]:
            self.attacking_player.statistics.passes_missed += 1
            self.commentary.append(f"{self.attacking_player} failed to pass the ball!")
            if self.outcome == EventOutcome.PASS_INTERCEPT:
                self.defending_player.statistics.interceptions += 1
            if self.outcome == EventOutcome.PASS_OFFSIDE:
                attacking_team.stats.offsides += 1
                self.commentary.append(f"{self.receiving_player} was offside!")
            self.attacking_player.received_ball = None
            self.defending_player.received_ball = None
            self.receiving_player.received_ball = None
            self.state = self.change_possession(
                attacking_team, defending_team, self.defending_player, end_position
            )
        else:
            self.state.position = end_position
            self.commentary.append(
                f"{self.attacking_player} passed the ball to {self.receiving_player}"
            )
            self.attacking_player.received_ball = None
            self.receiving_player.received_ball = self.attacking_player
            self.defending_player.received_ball = None
            attacking_team.player_in_possession = self.receiving_player

        attacking_team.update_stats()
        defending_team.update_stats()
        return self.state
