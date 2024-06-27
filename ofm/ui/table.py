import tkinter as tk
import ttkbootstrap as ttk


class AutoResizeTreeview(ttk.Treeview):
    def __init__(self, master=None, columns=None, rows=None, **kwargs):
        super().__init__(master, columns=columns, selectmode="browse", **kwargs)
        self._init_columns(columns)
        if rows:
            self.add_rows(rows)
        self.bind("<ButtonRelease-1>", self.on_column_resize)

    def _init_columns(self, columns):
        for col in columns:
            self.heading(col, text=col)
            self.column(col, width=100)  # Default width

    def on_column_resize(self, event):
        for col in self["columns"]:
            self.auto_size_column(col)

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
