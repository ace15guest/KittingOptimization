import datetime
import tkinter as tk
from itertools import count
from logging import exception
from pydoc_data.topics import topics
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import sqlalchemy.exc
from PIL import Image, ImageTk
import json
import os
import tkinter
import database
import ast
import matching_algos
from interface import mirror_coordinates
import global_vars.vars
import global_vars.funcs
import settings_lib

class OptimizationApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel Matching Optimization")
        self.window_width = 900
        self.window_height = 800
        self.root.geometry(f"{self.window_width}x{self.window_height}")

        # Database
        database.create_db()
        Session = database.sessionmaker(bind=database.engine)
        self.db_session = Session()

        # TKinter vars
        self.pn_var_dropdown_opt = ctk.StringVar()

        self.create_interface()

        self.root.mainloop()

    def create_interface(self):
        # Create dropdown
        self.part_number_dropdown = ctk.CTkComboBox(self.root, variable=self.pn_var_dropdown_opt, state='readonly', values=[])
        self.part_number_dropdown.pack()

        # Optimize Button
        optimize_btn = ctk.CTkButton(self.root, text="Optimize", command=self.optimize_button_clicked)
        optimize_btn.pack()

        self.scroll_canvas = ctk.CTkCanvas(self.root, width=300, height=300)

        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        # Add Table to canvas
        self.optimize_table = ttk.Treeview(self.scroll_canvas, height=35)
        self.optimize_table.pack()
        self.optimize_table.tag_configure('used', background='light green')
        self.optimize_table.tag_configure('unused', background='white')
        # Add Export Button
        export_btn = ctk.CTkButton(self.root, text="Export", command=self.export_optimization)
        export_btn.pack()

        self.add_pns_to_opt_dropdown()
        # Menu Bar
        menubar = tkinter.Menu(self.root)
        self.root.configure(menu=menubar)

        settings_menu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Edit', menu=settings_menu)

        settings_menu.add_command(label="Settings", command=global_vars.funcs.open_settings_window)

    def add_pns_to_opt_dropdown(self):
        col_name = database.Part.PartNumber
        stmt = database.select(col_name).distinct()
        distinct_values = self.db_session.execute(stmt).scalars().all()
        self.part_number_dropdown.configure(values=distinct_values)
        return
    def optimize_button_clicked(self):
        self.optimized_layer_df = matching_algos.separate_layers(self.part_number_dropdown.get(), self.db_session)
        layer_names = ast.literal_eval(self.db_session.query(database.Part).filter_by(PartNumber=self.pn_var_dropdown_opt.get()).first().LayerNames.strip())
        # Delete Treeview items
        for item in self.optimize_table.get_children():
            self.optimize_table.delete(item)
        header_names = []
        for name in layer_names:
            header_names.append(f"Shop Order {name}")
            header_names.append(f"Panel {name}")

        header_names.append("Percent Yield")
        header_names.append("Used")
        self.optimize_table['columns'] = (header_names)

        # Add Layer optimized Layers
        for name in layer_names:
            self.optimize_table.heading(f'Shop Order {name}', text=f"Shop Order {name}")
            self.optimize_table.column(f'Shop Order {name}', stretch=False, width=100)
            self.optimize_table.heading(f'Panel {name}', text =f"Panel {name}")
            self.optimize_table.column(f'Panel {name}', stretch=False, width=100)


        self.optimize_table.heading('Percent Yield', text="% Yield")
        self.optimize_table.column(f'Percent Yield', stretch=False, width=100)
        self.optimize_table.heading('Used', text="Used")
        self.optimize_table.column(f'Used', stretch=False, width=100)
        count = 0
        for idx, row in self.optimized_layer_df.iterrows():
            information = []
            count+=1
            for layer in layer_names:
                info = row[layer].split('_')
                self.optimized_pn = info[0]
                shop_order = info[1]
                img_num = info[2]
                layer = info[3]
                information.append(shop_order)
                information.append(img_num)
            perc_yield = row['Percent Yield']
            num_wasted = row["Number Wasted"]
            information.append(perc_yield)
            information.append("False")
            self.optimize_table.insert("", "end", values=tuple(information))

        self.optimize_table["show"] = 'headings'

        self.optimize_table.bind("<<TreeviewSelect>>", self.toggle_text)
        self.scroll_canvas.update_idletasks()
        self.scroll_canvas.config(self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        if count == 0:
            messagebox.showerror('No Data', "There are not enough panels to create an optimization.")

    def toggle_text(self, event):
        try:
            item_id = self.optimize_table.selection()[-1]
        except IndexError:
            return

        item_values = self.optimize_table.item(item_id, "values")  # Get the current values

        # Toggle the text for the first column
        new_text = "True" if item_values[-1] != "True" else "False"
        tags = 'used' if new_text == "True" else 'unused'
        self.optimize_table.item(item_id, values=(*item_values[:-1], new_text), tags=(tags))
        self.optimize_table.selection_remove(self.optimize_table.selection())
        return

    def export_optimization(self):
        used = [self.optimize_table.set(item, 'Used') for item in self.optimize_table.get_children()]
        self.optimized_layer_df['Used'] = used
        folder = filedialog.askdirectory()
        path = f'{folder}/{self.optimized_pn}_optimized_{datetime.datetime.today().month}_{datetime.datetime.today().day}_{datetime.datetime.today().year}.csv'

        try:
            self.optimized_layer_df.to_csv(path)
        except PermissionError:
            messagebox.showerror('Permission Error', f"{path} is unable to be accessed")
        count = 0
        try:
            count = self.delete_used_panels()
            self.db_session.commit() # Commit the changes to the database
        except Exception as error:
            messagebox.showerror('Deletion Error', 'The used combinations were unable to be deleted from the database.')
            return

        messagebox.showinfo('Success', f'Updates to the database have been made successfully. {count} items have been deleted from the database')

    def delete_used_panels(self):
        used_df = self.optimized_layer_df[self.optimized_layer_df['Used'] == 'True']
        layer_names = ast.literal_eval(self.db_session.query(database.Part).filter_by(PartNumber=self.optimized_pn).first().LayerNames.strip())
        count = 0
        for idx, row in used_df.iterrows():
            for layer in layer_names:
                info = row[layer].split('_')
                shop_order = info[1]
                img_num = info[2]
                layer = info[3]
                matches = self.db_session.query(database.ShopOrder).filter_by(ShopOrderNumber=shop_order, PartNumber=self.optimized_pn, LayerNumber=layer, PanelNumber=img_num).all()
                for match in matches:
                    self.db_session.delete(match)
                    count += 1
        return count
