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
import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class OffensiveAttributesFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.offensive_label = ttk.Label(
            self, text="Offensive Attributes", font=("Helvetica", 16)
        )
        self.offensive_label.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)

        self.shot_power_value = ttk.IntVar()
        self.shot_accuracy_value = ttk.IntVar()
        self.free_kick_value = ttk.IntVar()
        self.penalty_value = ttk.IntVar()
        self.positioning_value = ttk.IntVar()

        self.shot_power_label = ttk.Label(
            self, text="Shot Power: ", font=("Helvetica", 12)
        )
        self.shot_accuracy_label = ttk.Label(
            self, text="Shot Accuracy: ", font=("Helvetica", 12)
        )
        self.free_kick_label = ttk.Label(
            self, text="Free Kick: ", font=("Helvetica", 12)
        )
        self.penalty_label = ttk.Label(self, text="Penalty: ", font=("Helvetica", 12))
        self.positioning_label = ttk.Label(
            self, text="Positioning: ", font=("Helvetica", 12)
        )

        self.shot_power_value_label = ttk.Label(
            self, textvariable=self.shot_power_value, font=("Helvetica", 12)
        )
        self.shot_accuracy_value_label = ttk.Label(
            self, textvariable=self.shot_accuracy_value, font=("Helvetica", 12)
        )
        self.free_kick_value_label = ttk.Label(
            self, textvariable=self.free_kick_value, font=("Helvetica", 12)
        )
        self.penalty_value_label = ttk.Label(
            self, textvariable=self.penalty_value, font=("Helvetica", 12)
        )
        self.positioning_value_label = ttk.Label(
            self, textvariable=self.positioning_value, font=("Helvetica", 12)
        )

        self.shot_power_label.grid(row=1, column=0, padx=5, pady=10, sticky=NSEW)
        self.shot_accuracy_label.grid(row=2, column=0, padx=5, pady=10, sticky=NSEW)
        self.free_kick_label.grid(row=3, column=0, padx=5, pady=10, sticky=NSEW)
        self.penalty_label.grid(row=4, column=0, padx=5, pady=10, sticky=NSEW)
        self.positioning_label.grid(row=5, column=0, padx=5, pady=10, sticky=NSEW)

        self.shot_power_value_label.grid(row=1, column=1, padx=5, pady=10, sticky=NSEW)
        self.shot_accuracy_value_label.grid(
            row=2, column=1, padx=5, pady=10, sticky=NSEW
        )
        self.free_kick_value_label.grid(row=3, column=1, padx=5, pady=10, sticky=NSEW)
        self.penalty_value_label.grid(row=4, column=1, padx=5, pady=10, sticky=NSEW)
        self.positioning_value_label.grid(row=5, column=1, padx=5, pady=10, sticky=NSEW)


class DefensiveAttributesFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.defensive_label = ttk.Label(
            self, text="Defensive Attributes", font=("Helvetica", 16)
        )
        self.defensive_label.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)

        self.tackling_value = ttk.IntVar()
        self.interception_value = ttk.IntVar()
        self.positioning_value = ttk.IntVar()

        self.tackling_label = ttk.Label(self, text="Tackling: ", font=("Helvetica", 12))
        self.interception_label = ttk.Label(
            self, text="Interception: ", font=("Helvetica", 12)
        )
        self.positioning_label = ttk.Label(
            self, text="Positioning: ", font=("Helvetica", 12)
        )

        self.tackling_value_label = ttk.Label(
            self, textvariable=self.tackling_value, font=("Helvetica", 12)
        )
        self.interception_value_label = ttk.Label(
            self, textvariable=self.interception_value, font=("Helvetica", 12)
        )
        self.positioning_value_label = ttk.Label(
            self, textvariable=self.positioning_value, font=("Helvetica", 12)
        )

        self.tackling_label.grid(row=1, column=0, padx=5, pady=10, sticky=NSEW)
        self.interception_label.grid(row=2, column=0, padx=5, pady=10, sticky=NSEW)
        self.positioning_label.grid(row=3, column=0, padx=5, pady=10, sticky=NSEW)

        self.tackling_value_label.grid(row=1, column=1, padx=5, pady=10, sticky=NSEW)
        self.interception_value_label.grid(
            row=2, column=1, padx=5, pady=10, sticky=NSEW
        )
        self.positioning_value_label.grid(row=3, column=1, padx=5, pady=10, sticky=NSEW)


class IntelligenceAttributesFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.intelligence_label = ttk.Label(
            self, text="Intelligence Attributes", font=("Helvetica", 16)
        )
        self.intelligence_label.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)

        self.vision_value = ttk.IntVar()
        self.passing_value = ttk.IntVar()
        self.dribbling_value = ttk.IntVar()
        self.crossing_value = ttk.IntVar()
        self.ball_control_value = ttk.IntVar()
        self.dribbling_value = ttk.IntVar()
        self.skills_value = ttk.IntVar()
        self.team_work_value = ttk.IntVar()

        self.vision_label = ttk.Label(self, text="Vision: ", font=("Helvetica", 12))
        self.passing_label = ttk.Label(self, text="Passing: ", font=("Helvetica", 12))
        self.dribbling_label = ttk.Label(
            self, text="Dribbling: ", font=("Helvetica", 12)
        )
        self.crossing_label = ttk.Label(self, text="Crossing: ", font=("Helvetica", 12))
        self.ball_control_label = ttk.Label(
            self, text="Ball Control: ", font=("Helvetica", 12)
        )
        self.dribbling_label = ttk.Label(
            self, text="Dribbling: ", font=("Helvetica", 12)
        )
        self.skills_label = ttk.Label(self, text="Skills: ", font=("Helvetica", 12))
        self.team_work_label = ttk.Label(
            self, text="Team Work: ", font=("Helvetica", 12)
        )

        self.vision_value_label = ttk.Label(
            self, textvariable=self.vision_value, font=("Helvetica", 12)
        )
        self.passing_value_label = ttk.Label(
            self, textvariable=self.passing_value, font=("Helvetica", 12)
        )
        self.dribbling_value_label = ttk.Label(
            self, textvariable=self.dribbling_value, font=("Helvetica", 12)
        )
        self.crossing_value_label = ttk.Label(
            self, textvariable=self.crossing_value, font=("Helvetica", 12)
        )
        self.ball_control_value_label = ttk.Label(
            self, textvariable=self.ball_control_value, font=("Helvetica", 12)
        )

        self.vision_label.grid(row=1, column=0, padx=5, pady=10, sticky=NSEW)
        self.passing_label.grid(row=2, column=0, padx=5, pady=10, sticky=NSEW)
        self.dribbling_label.grid(row=3, column=0, padx=5, pady=10, sticky=NSEW)
        self.crossing_label.grid(row=4, column=0, padx=5, pady=10, sticky=NSEW)
        self.ball_control_label.grid(row=5, column=0, padx=5, pady=10, sticky=NSEW)

        self.vision_value_label.grid(row=1, column=1, padx=5, pady=10, sticky=NSEW)
        self.passing_value_label.grid(row=2, column=1, padx=5, pady=10, sticky=NSEW)
        self.dribbling_value_label.grid(row=3, column=1, padx=5, pady=10, sticky=NSEW)
        self.crossing_value_label.grid(row=4, column=1, padx=5, pady=10, sticky=NSEW)
        self.ball_control_value_label.grid(
            row=5, column=1, padx=5, pady=10, sticky=NSEW
        )


class PhysicalAttributesFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.physical_label = ttk.Label(
            self, text="Physical Attributes", font=("Helvetica", 16)
        )
        self.physical_label.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)

        self.strength_value = ttk.IntVar()
        self.aggression_value = ttk.IntVar()
        self.endurance_value = ttk.IntVar()

        self.strength_label = ttk.Label(self, text="Strength: ", font=("Helvetica", 12))
        self.aggression_label = ttk.Label(
            self, text="Aggression: ", font=("Helvetica", 12)
        )
        self.endurance_label = ttk.Label(
            self, text="Endurance: ", font=("Helvetica", 12)
        )

        self.strength_value_label = ttk.Label(
            self, textvariable=self.strength_value, font=("Helvetica", 12)
        )
        self.aggression_value_label = ttk.Label(
            self, textvariable=self.aggression_value, font=("Helvetica", 12)
        )
        self.endurance_value_label = ttk.Label(
            self, textvariable=self.endurance_value, font=("Helvetica", 12)
        )

        self.strength_label.grid(row=1, column=0, padx=5, pady=10, sticky=NSEW)
        self.aggression_label.grid(row=2, column=0, padx=5, pady=10, sticky=NSEW)
        self.endurance_label.grid(row=3, column=0, padx=5, pady=10, sticky=NSEW)

        self.strength_value_label.grid(row=1, column=1, padx=5, pady=10, sticky=NSEW)
        self.aggression_value_label.grid(row=2, column=1, padx=5, pady=10, sticky=NSEW)
        self.endurance_value_label.grid(row=3, column=1, padx=5, pady=10, sticky=NSEW)


class GkAttributesFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gk_attributes_label = ttk.Label(
            self, text="GK Attributes", font=("Helvetica", 16)
        )
        self.gk_attributes_label.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)

        self.reflexes_value = ttk.IntVar()
        self.jumping_value = ttk.IntVar()
        self.positioning_value = ttk.IntVar()
        self.penalty_value = ttk.IntVar()

        self.reflexes_label = ttk.Label(self, text="Reflexes: ", font=("Helvetica", 12))
        self.jumping_label = ttk.Label(self, text="Jumping: ", font=("Helvetica", 12))
        self.positioning_label = ttk.Label(
            self, text="Positioning: ", font=("Helvetica", 12)
        )
        self.penalty_label = ttk.Label(self, text="Penalty: ", font=("Helvetica", 12))

        self.reflexes_value_label = ttk.Label(
            self, textvariable=self.reflexes_value, font=("Helvetica", 12)
        )
        self.jumping_value_label = ttk.Label(
            self, textvariable=self.jumping_value, font=("Helvetica", 12)
        )
        self.positioning_value_label = ttk.Label(
            self, textvariable=self.positioning_value, font=("Helvetica", 12)
        )
        self.penalty_value_label = ttk.Label(
            self, textvariable=self.penalty_value, font=("Helvetica", 12)
        )

        self.reflexes_label.grid(row=1, column=0, padx=5, pady=10, sticky=NSEW)
        self.jumping_label.grid(row=2, column=0, padx=5, pady=10, sticky=NSEW)
        self.positioning_label.grid(row=3, column=0, padx=5, pady=10, sticky=NSEW)
        self.penalty_label.grid(row=4, column=0, padx=5, pady=10, sticky=NSEW)

        self.reflexes_value_label.grid(row=1, column=1, padx=5, pady=10, sticky=NSEW)
        self.jumping_value_label.grid(row=2, column=1, padx=5, pady=10, sticky=NSEW)
        self.positioning_value_label.grid(row=3, column=1, padx=5, pady=10, sticky=NSEW)
        self.penalty_value_label.grid(row=4, column=1, padx=5, pady=10, sticky=NSEW)


class PlayerProfilePage(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player_choice_frame = ttk.Frame(self)
        self.player_details_frame = ttk.Frame(self)

        self.player_list = ttk.Variable(
            value=["Allejo", "Ronaldo", "Ronaldinho", "Messi", "Suarez", "Neymar"]
        )
        self.player_choice = tk.Listbox(
            self.player_choice_frame, listvariable=self.player_list
        )
        self.player_choice.selection_set(0)
        self.player_choice.pack(side=LEFT, fill=BOTH, expand=True)

        # PLAYER DETAILS

        self.player_personal_info_frame = ttk.Frame(self.player_details_frame)

        self.player_image = ttk.PhotoImage(file="ofm/res/images/placeholder.png")
        self.player_image = self.player_image.subsample(5, 5)
        width = self.player_image.width()
        height = self.player_image.height()

        self.canvas = ttk.Canvas(self.player_personal_info_frame)
        self.canvas.create_image(0, 0, image=self.player_image, anchor=NW)
        self.canvas.config(width=width, height=height)
        self.canvas.grid(row=0, rowspan=5, column=0, padx=10, pady=10, sticky=NSEW)

        self.player_name_value = ttk.StringVar(value="Allejo")

        self.player_name_label = ttk.Label(
            self.player_personal_info_frame,
            textvariable=self.player_name_value,
            font=("Helvetica", 20),
        )
        self.player_name_label.grid(row=0, column=1, padx=20, pady=10, sticky=NSEW)

        self.player_personal_details_frame = ttk.Frame(self.player_personal_info_frame)
        self.player_birth_date_label = ttk.Label(
            self.player_personal_details_frame,
            text="Birth date: ",
            font=("Helvetica", 12),
        )
        self.player_birth_date_label.grid(
            row=0, column=0, padx=20, pady=10, sticky=NSEW
        )

        self.player_birth_date_value = ttk.StringVar(value="22-09-1995")

        self.player_birth_date_label = ttk.Label(
            self.player_personal_details_frame,
            textvariable=self.player_birth_date_value,
            font=("Helvetica", 12),
        )
        self.player_birth_date_label.grid(
            row=0, column=1, padx=10, pady=10, sticky=NSEW
        )

        self.player_nationality_label = ttk.Label(
            self.player_personal_details_frame,
            text="Nationality: ",
            font=("Helvetica", 12),
        )
        self.player_nationality_label.grid(
            row=1, column=0, padx=20, pady=10, sticky=NSEW
        )

        self.player_nationality_value = ttk.StringVar(value="Brazil")

        self.player_nationality_value_label = ttk.Label(
            self.player_personal_details_frame,
            textvariable=self.player_nationality_value,
            font=("Helvetica", 12),
        )
        self.player_nationality_value_label.grid(
            row=1, column=1, padx=10, pady=10, sticky=NSEW
        )

        self.positions_value = ttk.StringVar(value="FW")

        self.positions_label = ttk.Label(
            self.player_personal_details_frame,
            text="Positions: ",
            font=("Helvetica", 12),
        )
        self.positions_label.grid(row=2, column=0, padx=20, pady=10, sticky=NSEW)

        self.positions_value_label = ttk.Label(
            self.player_personal_details_frame,
            textvariable=self.positions_value,
            font=("Helvetica", 12),
        )
        self.positions_value_label.grid(row=2, column=1, padx=10, pady=10, sticky=NSEW)

        self.player_personal_details_frame.grid(
            row=1, column=1, padx=10, pady=10, sticky=NSEW
        )
        self.player_personal_info_frame.grid(
            row=0, column=0, columnspan=3, padx=10, pady=10, sticky=NSEW
        )

        self.player_attributes_frame = ttk.Frame(
            self.player_details_frame, relief=RAISED, borderwidth=1
        )
        self.player_attributes_frame.grid(
            row=4, column=0, columnspan=3, padx=20, pady=10, sticky=NSEW
        )

        self.offensive_attributes_column = OffensiveAttributesFrame(
            self.player_attributes_frame
        )
        self.offensive_attributes_column.grid(
            row=0, column=0, padx=10, pady=10, sticky=NSEW
        )

        self.defensive_attributes_column = DefensiveAttributesFrame(
            self.player_attributes_frame
        )
        self.defensive_attributes_column.grid(
            row=0, column=1, padx=10, pady=10, sticky=NSEW
        )

        self.physical_attributes_column = PhysicalAttributesFrame(
            self.player_attributes_frame
        )
        self.physical_attributes_column.grid(
            row=0, column=2, padx=10, pady=10, sticky=NSEW
        )

        self.intelligence_attributes_column = IntelligenceAttributesFrame(
            self.player_attributes_frame
        )
        self.intelligence_attributes_column.grid(
            row=1, column=0, padx=10, pady=10, sticky=NSEW
        )

        self.gk_attributes_column = GkAttributesFrame(self.player_attributes_frame)
        self.gk_attributes_column.grid(row=1, column=1, padx=10, pady=10, sticky=NSEW)

        self.player_choice_frame.grid(
            row=0, column=0, rowspan=3, padx=20, pady=20, sticky=NSEW
        )
        self.player_details_frame.grid(row=0, column=1, padx=20, pady=20, sticky=NSEW)

        self.button_frame = ttk.Frame(self)

        self.cancel_btn = ttk.Button(self.button_frame, text="Cancel")
        self.cancel_btn.pack(fill=BOTH, side=BOTTOM, padx=20, pady=20)

        self.button_frame.grid(
            row=1, column=0, columnspan=4, padx=20, pady=20, sticky=NSEW
        )
