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
from ttkbootstrap.tableview import Tableview


class TeamExplorerPage(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title_label = ttk.Label(self, text="Team Explorer", font="Arial 24 bold")
        self.title_label.grid(
            row=0, column=0, padx=10, pady=10, columnspan=2, sticky=NS
        )

        self.team_details = ttk.Frame(self)
        default_regions = ["UEFA", "CONMEBOL", "CAF", "AFC"]
        self.region_selection_variable = ttk.StringVar(value=default_regions[0])
        self.region_selection = ttk.Combobox(
            self.team_details,
            textvariable=self.region_selection_variable,
            values=default_regions,
            state="readonly",
        )
        self.region_selection.grid(row=0, column=0, padx=10, pady=10, sticky=EW)

        default_countries = ["Spain", "Germany", "England", "France"]
        self.country_selection_variable = ttk.StringVar(value=default_countries[0])
        self.country_selection = ttk.Combobox(
            self.team_details,
            textvariable=self.country_selection_variable,
            values=default_countries,
            state="readonly",
        )
        self.country_selection.set("Spain")
        self.country_selection.grid(row=1, column=0, padx=10, pady=10, sticky=EW)

        self.team_selection_items = tk.Variable(
            value=["Team 1", "Team 2", "Team 3", "Team 4", "Team 5"]
        )
        self.team_selection = tk.Listbox(
            self.team_details,
            height=15,
            width=30,
            listvariable=self.team_selection_items,
            selectmode=ttk.BROWSE,
        )
        self.team_selection.selection_set(0)
        self.team_selection.grid(
            row=2, column=0, rowspan=2, padx=10, pady=10, sticky=EW
        )

        self.columns = [
            {"text": "Name", "stretch": False},
            {"text": "Nationality", "stretch": False},
            {"text": "Age", "stretch": False},
            {"text": "Position", "stretch": False},
            {"text": "Overall", "stretch": False},
        ]

        home_rows = [
            ("Gomez", "Brazil", "25", "FW", "89"),
            ("Allejo", "Brazil", "22", "FW", "95"),
            ("Beranco", "Brazil", "28", "MF", "85"),
            ("Pardilla", "Brazil", "29", "MF", "83"),
            ("Santos", "Brazil", "24", "MF", "80"),
            ("Ferreira", "Brazil", "21", "MF", "87"),
            ("Roca", "Brazil", "25", "DF", "86"),
            ("Vincento", "Brazil", "32", "DF", "84"),
            ("Cicero", "Brazil", "26", "DF", "90"),
            ("Marengez", "Brazil", "27", "DF", "88"),
            ("Da Silva", "Brazil", "35", "GK", "92"),
        ]

        self.team_table = Tableview(
            self,
            coldata=self.columns,
            rowdata=home_rows,
            searchable=False,
            autofit=True,
            paginated=False,
            pagesize=8,
            height=18,
        )
        self.team_table.grid(row=0, column=1, rowspan=4, padx=10, pady=10, sticky=EW)

        self.team_details.grid(row=1, column=0, padx=10, pady=10, sticky=NS)

        self.button_frame = ttk.Frame(self)

        self.cancel_btn = ttk.Button(self.button_frame, text="Cancel")
        self.cancel_btn.pack(side="left", padx=10)

        self.button_frame.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky=NS
        )
