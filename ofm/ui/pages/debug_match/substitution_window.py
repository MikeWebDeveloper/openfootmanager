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
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import Messagebox, MessageCatalog

from ofm.ui.table import AutoResizeTreeview


class CornerKickTab(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.columns = ["Name", "Corner Kick", "Passing", "Crossing"]
        rows = [
            ("Gomez", "78", "88", "87"),
            ("Allejo", "95", "87", "97"),
            ("Beranco", "99", "83", "85"),
            ("Pardilla", "82", "79", "84"),
            ("Santos", "83", "78", "83"),
            ("Ferreira", "77", "78", "79"),
            ("Roca", "83", "87", "84"),
            ("Vincento", "65", "75", "70"),
            ("Cicero", "68", "88", "46"),
            ("Marengez", "55", "55", "78"),
            ("Da Silva", "32", "50", "45"),
        ]

        self.team_table = AutoResizeTreeview(
            self,
            columns=self.columns,
            rows=rows,
            height=11,
            show="headings",
        )

        self.corner_kick_taker_label = ttk.Label(self, text="Corner Kick Taker: ")
        self.corner_kick_taker = ttk.StringVar()

        self.team_table.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW
        )
        self.corner_kick_taker_label.grid(
            row=1, column=0, padx=10, pady=10, sticky=NSEW
        )

    def update_players(self, players: list[tuple[str, str, str, str]]):
        self.team_table.delete(*self.team_table.get_children())
        self.team_table.add_rows(players)

    def update_taker(self, player: str):
        self.corner_kick_taker.set(player)
        self.corner_kick_taker_label["text"] = f"Corner Kick Taker: {player}"


class PenaltyKickTab(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.columns = ["Name", "Penalty", "Shooting"]
        rows = [
            ("Gomez", "78", "87"),
            ("Allejo", "95", "97"),
            ("Beranco", "99", "85"),
            ("Pardilla", "82", "84"),
            ("Santos", "83", "83"),
            ("Ferreira", "77", "79"),
            ("Roca", "83", "84"),
            ("Vincento", "65", "70"),
            ("Cicero", "68", "46"),
            ("Marengez", "55", "78"),
            ("Da Silva", "32", "45"),
        ]

        self.team_table = AutoResizeTreeview(
            self,
            columns=self.columns,
            rows=rows,
            height=11,
            show="headings",
        )

        self.penalty_kick_taker_label = ttk.Label(self, text="Penalty Kick Taker: ")
        self.penalty_kick_taker = ttk.StringVar()

        self.team_table.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW
        )
        self.penalty_kick_taker_label.grid(
            row=1, column=0, padx=10, pady=10, sticky=NSEW
        )

    def update_players(self, players: list[tuple[str, str, str, str]]):
        self.team_table.delete(*self.team_table.get_children())
        self.team_table.add_rows(players)

    def update_taker(self, player: str):
        self.penalty_kick_taker.set(player)
        self.penalty_kick_taker_label["text"] = f"Penalty Kick Taker: {player}"


class FreeKickTab(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.columns = ["Name", "Free Kick", "Passing", "Shooting"]
        rows = [
            ("Gomez", "78", "88", "87"),
            ("Allejo", "95", "87", "97"),
            ("Beranco", "99", "83", "85"),
            ("Pardilla", "82", "79", "84"),
            ("Santos", "83", "78", "83"),
            ("Ferreira", "77", "78", "79"),
            ("Roca", "83", "87", "84"),
            ("Vincento", "65", "75", "70"),
            ("Cicero", "68", "88", "46"),
            ("Marengez", "55", "55", "78"),
            ("Da Silva", "32", "50", "45"),
        ]

        self.team_table = AutoResizeTreeview(
            self,
            columns=self.columns,
            rows=rows,
            height=11,
            show="headings",
        )

        self.free_kick_taker_label = ttk.Label(self, text="Free Kick Taker: ")
        self.free_kick_taker = ttk.StringVar()

        self.team_table.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW
        )
        self.free_kick_taker_label.grid(row=1, column=0, padx=10, pady=10, sticky=NSEW)

    def update_players(self, players: list[tuple[str, str, str, str]]):
        self.team_table.delete(*self.team_table.get_children())
        self.team_table.add_rows(players)

    def update_taker(self, player: str):
        self.free_kick_taker.set(player)
        self.free_kick_taker_label["text"] = f"Free Kick Taker: {player}"


class SubstitutionTab(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_frame = ttk.Frame(self)

        self.columns = [
            "Name",
            "Position",
            "Stamina",
            "Injured",
            "Overall",
        ]

        rows = [
            ("Gomez", "FW", "100", "No", "89"),
            ("Allejo", "FW", "100", "No", "95"),
            ("Beranco", "MF", "100", "No", "85"),
            ("Pardilla", "MF", "100", "No", "83"),
            ("Santos", "MF", "100", "No", "80"),
            ("Ferreira", "MF", "100", "No", "87"),
            ("Roca", "DF", "100", "No", "86"),
            ("Vincento", "DF", "100", "No", "84"),
            ("Cicero", "DF", "100", "No", "90"),
            ("Marengez", "DF", "100", "No", "88"),
            ("Da Silva", "GK", "100", "No", "92"),
        ]

        self.team_table = AutoResizeTreeview(
            self.main_frame,
            columns=self.columns,
            rows=rows,
            height=11,
            show="headings",
        )

        self.formation_label = ttk.Label(self.main_frame, text="Formation: ")
        self.formation_combobox = ttk.Combobox(self.main_frame, values=["4-4-2"])

        self.button_in = ttk.Button(self.main_frame, text=">")
        self.button_out = ttk.Button(self.main_frame, text="<")

        self.reserves_table = AutoResizeTreeview(
            self.main_frame,
            columns=self.columns,
            rows=rows,
            height=11,
            show="headings",
        )
        self.substitutions_left_label = ttk.Label(
            self.main_frame, text="Substitutions left: 0"
        )

        self.team_table.grid(row=0, rowspan=2, column=0, padx=10, pady=10, sticky=NSEW)
        self.button_in.grid(row=0, column=1, padx=10, pady=10, sticky=NS)
        self.button_out.grid(row=1, column=1, padx=10, pady=10, sticky=NS)
        self.reserves_table.grid(
            row=0, rowspan=2, column=2, padx=10, pady=10, sticky=NSEW
        )
        self.formation_label.grid(row=3, column=0, padx=10, pady=10, sticky=NSEW)
        self.formation_combobox.grid(
            row=2, column=1, columnspan=2, padx=10, pady=10, sticky=NSEW
        )
        self.substitutions_left_label.grid(
            row=3, column=0, columnspan=3, padx=10, pady=10, sticky=NSEW
        )

        self.main_frame.grid(row=0, column=0, sticky=NSEW)

    def update_formations(self, formations: list[str]):
        self.formation_combobox["values"] = formations

    def update_formation_box(self, formation: str):
        formations = self.formation_combobox["values"]
        if formation in formations:
            self.formation_combobox.set(formation)
        else:
            self.formation_combobox.set(formations[0])

    def update_team_table(self, players: list[tuple]):
        self.team_table.delete(*self.team_table.get_children())
        self.team_table.add_rows(players)

    def update_reserves_table(self, players: list[tuple]):
        self.reserves_table.delete(*self.reserves_table.get_children())
        self.reserves_table.add_rows(players)

    def update_substitution_amount(self, amount: int):
        self.substitutions_left_label["text"] = f"Substitutions left: {amount}"


class SubstitutionWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.wm_title("Substitute Players")
        self.resizable(False, False)
        self.geometry("")
        self.grab_set()

        self.notebook = ttk.Notebook(self)
        self.substitution_tab = SubstitutionTab(self.notebook)
        self.free_kick_tab = FreeKickTab(self.notebook)
        self.penalty_kick_tab = PenaltyKickTab(self.notebook)
        self.corner_kick_tab = CornerKickTab(self.notebook)

        self.team_name_variable = ttk.StringVar()
        self.team_name = ttk.Label(
            self,
            text="TeamName",
            font="Arial 18 bold",
            textvariable=self.team_name_variable,
        )

        self.team_name.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=NS)

        self.button_frame = ttk.Frame(self)
        self.apply_button = ttk.Button(self.button_frame, text="Apply")
        self.cancel_button = ttk.Button(self.button_frame, text="Cancel")

        self.notebook.add(self.substitution_tab, text="Substitution")
        self.notebook.add(self.free_kick_tab, text="Free Kick")
        self.notebook.add(self.penalty_kick_tab, text="Penalty Kick")
        self.notebook.add(self.corner_kick_tab, text="Corner Kick")

        self.notebook.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=NSEW)

        self.button_frame.grid(
            row=2, column=0, columnspan=3, padx=10, pady=10, sticky=NS
        )
        self.apply_button.grid(row=2, column=0, padx=10, pady=10, sticky=EW)
        self.cancel_button.grid(row=2, column=1, padx=10, pady=10, sticky=EW)

    def update_formations(self, formations: list[str]):
        self.substitution_tab.update_formations(formations)

    def update_formation_box(self, formation: str):
        self.substitution_tab.update_formation_box(formation)

    def cancel_dialog(self):
        return Messagebox.yesno(
            parent=self,
            title="Cancel formation",
            message="Are you sure you want to cancel the change? All changes will be lost.",
            alert=True,
        )

    def update_team_table(self, players: list[tuple]):
        self.substitution_tab.update_team_table(players)

    def update_reserves_table(self, players: list[tuple]):
        self.substitution_tab.update_reserves_table(players)

    def update_substitution_amount(self, amount: int):
        self.substitution_tab.update_substitution_amount(amount)

    def get_yes_result(self):
        return MessageCatalog.translate("Yes")

    def get_no_result(self):
        return MessageCatalog.translate("No")

    def update_team_name(self, team_name: str):
        self.team_name_variable.set(team_name)
