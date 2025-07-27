import tkinter as tk

import ttkbootstrap as ttk


class AutoResizeTreeview(ttk.Treeview):
    def __init__(self, master=None, columns=None, rows=None, **kwargs):
        super().__init__(master, columns=columns, selectmode="browse", **kwargs)
        self._init_columns(columns)
        if rows:
            self.add_rows(rows)
        self.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<B1-Motion>", self.on_motion)
        self.bind("<ButtonRelease-1>", self.on_button_release)
        self._is_resizing = False
        self._drag_data = {"item": None, "y": 0}

    def _init_columns(self, columns):
        for col in columns:
            self.heading(col, text=col)
            self.column(col, width=100)  # Default width

    def on_motion(self, event):
        if self._is_resizing:
            for col in self["columns"]:
                self.auto_size_column(col)

        if self._drag_data["item"]:
            delta_y = event.y - self._drag_data["y"]
            if abs(delta_y) > 5:
                self._drag_data["y"] = event.y
                self.move_item(event)

    def on_button_press(self, event):
        if self.identify_region(event.x, event.y) == "separator":
            self._is_resizing = True
        else:
            self._is_resizing = False
            item = self.identify_row(event.y)
            if item:
                self._drag_data["item"] = item
                self._drag_data["y"] = event.y

    def on_button_release(self, event):
        self._drag_data["item"] = None
        self._drag_data["y"] = 0
        self._is_resizing = False

    def move_item(self, event):
        y = event.y
        item_below = self.identify_row(y)
        if item_below and item_below != self._drag_data["item"]:
            index_below = self.index(item_below)
            item = self._drag_data["item"]
            if self.bbox(item_below)[1] < y:
                self.move(item, "", index_below)
            else:
                self.move(item, "", index_below + 1)

    def auto_size_column(self, col):
        max_width = tk.font.Font().measure(col)
        for item in self.get_children():
            cell_value = self.item(item, "values")[self["columns"].index(col)]
            cell_width = tk.font.Font().measure(cell_value)
            if cell_width > max_width:
                max_width = cell_width
        self.column(col, width=max_width + 10)  # Add padding

    def add_row(self, values):
        self.insert("", tk.END, values=values)
        for col in self["columns"]:
            self.auto_size_column(col)

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)
