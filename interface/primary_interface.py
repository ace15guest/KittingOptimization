import datetime
import tkinter as tk
from logging import exception
from pydoc_data.topics import topics
from tkinter import ttk, filedialog, messagebox

import sqlalchemy.exc
from PIL import Image, ImageTk
import json
import os
import database
import ast
import matching_algos
from interface import mirror_coordinates


#TODO: Clear out panel number
# TODO: Panel Layer double verification
class DefectMatchingApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel Matching Application")  # Name the application

        self.notebook = ttk.Notebook(self.root)  # Create notebook for tabs
        self.notebook.pack(expand=True, fill="both")  # Place the notebook into the screen

        # Initialize variables
        self.image_positions = {}  # Store image placements on the grid with rotation info
        self.rotation_angle = 0  # Track the current rotation angle of the image
        self.loaded_image = None  # Original loaded image
        self.image_file_path = None  # Store path of the currently loaded image
        self.image_thumbnails = []  # List to hold rotated thumbnails
        self.pn_layers = []  # Holds layers

        self.root.geometry("-2000+300")  # Where to open the application

        #Database connection
        Session = database.sessionmaker(bind=database.engine)
        self.db_session = Session()

        self.x_y_grid_count = 10
        self.canvas_size = 500
        self.grid_size = int(self.canvas_size/self.x_y_grid_count)
        # Input Vars
        self.pn_var_pct = tk.StringVar()

        self.shop_order_num_var = tk.StringVar()
        self.layer_num_var = tk.StringVar()
        self.pn_var_idt = tk.StringVar()
        self.panel_num_var = tk.StringVar()
        self.reverse_side_var = tk.IntVar()

        self.pn_var_dropdown_opt = tk.StringVar()

        # PCT Vars
        self.layer_name_var = tk.StringVar()
        self.pn_layers_var = tk.StringVar()

        # Set up tabs and widgets
        self.create_panel_creation_tab()
        self.create_image_defects_tab()
        self.create_optimization_tab()
    # Panel Creation

    def create_session(self):
        Session = database.sessionmaker(bind=database.engine)
        self.db_session = Session()

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

    def create_optimization_tab(self):
        self.optimization_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.optimization_tab, text="Optimization")
        # Create Dropdown
        self.part_number_dropdown = tk.ttk.Combobox(self.optimization_tab, textvariable=self.pn_var_dropdown_opt, state='readonly', values=[])
        # self.part_number_dropdown.grid(row=0, column=0)
        self.part_number_dropdown.pack()
        # Optimization
        optimize_btn = tk.Button(self.optimization_tab, text="Optimize", command=self.optimize_button_clicked)
        # optimize_btn.grid(row=0, column=1)
        optimize_btn.pack()

        # Add canvas for selecting

        self.scroll_canvas = tk.Canvas(self.optimization_tab, width=300, height=300)

        # self.scrollbar = tk.Scrollbar(self.optimization_tab, orient="vertical", command=self.scroll_canvas.yview)
        # self.scrollbar.pack(side="right", fill="y")
        #
        # self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        #
        # self.scroll_canvas.bind('<Configure>', lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox('all')))
        self.scroll_canvas.pack(side="left", fill="both", expand=True)


        # Add Table to canvas
        self.optimize_table = ttk.Treeview(self.scroll_canvas, height=35)
        self.optimize_table.pack()
        self.optimize_table.tag_configure('used', background='light green')
        self.optimize_table.tag_configure('unused', background='white')
        # Add Export Button
        export_btn = tk.Button(self.optimization_tab, text="Export", command=self.export_optimization)
        export_btn.pack()

        self.add_pns_to_opt_dropdown()

    def redraw_grid(self, canvas, reverse=False):
        self.grid_size = int(500 / self.x_y_grid_count)
        self.canvas_size = self.grid_size * self.x_y_grid_count
        canvas.config(height=self.canvas_size, width=self.canvas_size)
        color = 'gray'
        if reverse:
            color = 'red'
        self.draw_grid(canvas, color=color)

    def increase_grid(self):
        if self.x_y_grid_count >= 20:
            messagebox.showerror('Max Grid Reached', 'A 20 x 20 grid is the largest possible grid size')
            return
        self.x_y_grid_count+=1

        self.grid_size = int(500/self.x_y_grid_count)
        self.canvas_size = self.grid_size*self.x_y_grid_count
        self.canvas_pct.config(height=self.canvas_size, width=self.canvas_size)

        self.draw_grid(self.canvas_pct)

    def decrease_grid(self):
        if self.x_y_grid_count <= 2:
            messagebox.showerror('Min Grid Reached', 'A 2 x 2 grid is the smallest possible grid size')
            return
        self.x_y_grid_count -= 1
        self.grid_size = int(500 / self.x_y_grid_count)
        self.canvas_size = self.grid_size*self.x_y_grid_count
        self.canvas_pct.config(height=self.canvas_size, width=self.canvas_size)

        self.draw_grid(self.canvas_pct)

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
        for name in layer_names:
            self.optimize_table.heading(f'Shop Order {name}', text=f"Shop Order {name}")
            self.optimize_table.column(f'Shop Order {name}', stretch=False, width=100)
            self.optimize_table.heading(f'Panel {name}', text =f"Panel {name}")
            self.optimize_table.column(f'Panel {name}', stretch=False, width=100)


        self.optimize_table.heading('Percent Yield', text="% Yield")
        self.optimize_table.column(f'Percent Yield', stretch=False, width=100)
        self.optimize_table.heading('Used', text="Used")
        self.optimize_table.column(f'Used', stretch=False, width=100)
        for idx, row in self.optimized_layer_df.iterrows():
            information = []
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

    def toggle_text(self, event):
        try:
            item_id = self.optimize_table.selection()[-1]
        except IndexError:
            return

        item_values = self.optimize_table.item(item_id, "values")  # Get the current values

        # Toggle the text for the first column
        new_text = "True" if item_values[-1] != "True" else "False"
        tags = 'used' if new_text=="True" else 'unused'
        self.optimize_table.item(item_id, values=(*item_values[:-1], new_text), tags=(tags))
        self.optimize_table.selection_remove(self.optimize_table.selection())
        return

    def add_pns_to_opt_dropdown(self):
        col_name = database.Part.PartNumber
        stmt = database.select(col_name).distinct()
        distinct_values = self.db_session.execute(stmt).scalars().all()
        self.part_number_dropdown['values']=distinct_values
        return

    def create_panel_creation_tab(self):
        """Creates the Panel Creation tab and its components."""
        self.panel_creation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.panel_creation_tab, text="Panel Creation")

        # Part Number Entry
        part_label = tk.Label(self.panel_creation_tab, text="Part Number:")
        part_label.grid(row=0, column=1, pady=5)
        self.part_number_entry = tk.Entry(self.panel_creation_tab, textvariable=self.pn_var_pct, width=20)
        self.part_number_entry.grid(row=0, column=2, pady=5)
        # Reset Page
        reset = tk.Button(self.panel_creation_tab, text="Reset", command=self.reset_idt)
        reset.grid(row=0, column=3)
        # Image Upload Button
        upload_button = tk.Button(self.panel_creation_tab, text="Upload Image", command=self.upload_image)
        upload_button.grid(row=2, column=1, pady=20)

        # Add/Remove Layers
        self.add_button = tk.Button(self.panel_creation_tab, text="Add Layer", command=self.add_layer)
        self.add_button.grid(row=2, column=2, )
        self.remove_button = tk.Button(self.panel_creation_tab, text="Remove Layer", command=self.delete_layer)
        self.remove_button.grid(row=2, column=3)
        self.layer_name_entry = tk.Entry(self.panel_creation_tab, textvariable=self.layer_name_var)
        self.layer_name_entry.grid(row=2, column=4, padx=2)

        self.layer_names_entry = tk.Entry(self.panel_creation_tab, textvariable=self.pn_layers_var, width=50)
        self.layer_names_entry.grid(row=6, column=2, columnspan=3)

        # Image Display Label
        self.image_label = tk.Label(self.panel_creation_tab)
        self.image_label.grid(row=3, column=1, pady=20)

        # Rotate Button
        rotate_button = tk.Button(self.panel_creation_tab, text="Rotate Image 90°", command=self.rotate_image)
        rotate_button.grid(row=3, column=2, pady=5)

        # Save and Load Buttons
        save_button = tk.Button(self.panel_creation_tab, text="Save Positions", command=self.save_positions)
        save_button.grid(row=4, column=1, pady=5)
        load_button = tk.Button(self.panel_creation_tab, text="Load Positions", command=self.load_positions_pct)
        load_button.grid(row=4, column=2, pady=5)

        self.increase_grid_button = tk.Button(self.panel_creation_tab, text="Increase Grids", command=self.increase_grid)
        self.increase_grid_button.grid(row=4, column=3)
        self.decrease_grid_button = tk.Button(self.panel_creation_tab, text="Decrease Grids", command=self.decrease_grid)
        self.decrease_grid_button.grid(row=4, column=4)

        # Grid Canvas
        self.canvas_for_pct()

    def canvas_for_pct(self):
        self.canvas_pct = tk.Canvas(self.panel_creation_tab, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas_pct.grid(row=6, column=1, pady=20)
        self.canvas_pct.bind("<Button-1>", self.place_image_on_grid)

        self.draw_grid(self.canvas_pct)

    def add_layer(self):

        if self.layer_name_entry.get() == "":
            return
        self.pn_layers.append(self.layer_name_entry.get())
        self.layer_names_entry.delete(0, tk.END)



        self.layer_names_entry.insert(0, str(self.pn_layers))
        return

    def delete_layer(self):
        self.pn_layers = self.pn_layers[0:-1]
        self.layer_names_entry.delete(0, tk.END)

        self.layer_names_entry.insert(0, str(self.pn_layers))

        return

    def upload_image(self):
        """Handles uploading an image and prepares it for display."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp")])
        if file_path:
            self.image_file_path = file_path
            self.loaded_image = Image.open(self.image_file_path)
            self.rotation_angle = 0  # Reset rotation on new image
            self.apply_rotation()
            self.increase_grid_button.config(state=tk.DISABLED)
            self.decrease_grid_button.config(state=tk.DISABLED)

    def apply_rotation(self):
        """Applies the current rotation to the loaded image and updates the display."""
        if self.loaded_image:
            rotated_image = self.loaded_image.rotate(self.rotation_angle, expand=True).resize((self.grid_size, self.grid_size))
            thumbnail = ImageTk.PhotoImage(rotated_image)
            self.image_thumbnails.append(thumbnail)  # Store each rotated instance
            self.image_label.config(image=thumbnail)
            self.image_label.image = thumbnail  # Keep a reference to avoid garbage collection

    def rotate_image(self):
        """Rotates the loaded image by 90 degrees."""
        if self.loaded_image:
            self.rotation_angle = (self.rotation_angle + 90) % 360
            self.apply_rotation()
        else:
            messagebox.showwarning("Warning", "No image uploaded to rotate.")

    def draw_grid(self, canvas_used, color='gray'):
        """Draws the grid on the canvas_pct."""
        grid_size = self.grid_size
        canvas_used.delete('all')
        for x in range(0, self.canvas_size, grid_size):
            canvas_used.create_line(x, 0, x, 500, fill=color)
        for y in range(0, self.canvas_size, grid_size):
            canvas_used.create_line(0, y, self.canvas_size, y, fill=color)

    def place_image_on_grid(self, event):
        """Places the rotated image thumbnail on the grid without clearing existing placements."""
        if self.image_thumbnails and self.image_file_path:
            grid_size = self.grid_size
            x = (event.x // grid_size) * grid_size
            y = (event.y // grid_size) * grid_size
            position = f"{x},{y}"

            # Remove image if it exists at this position
            if position in self.image_positions:
                self.canvas_pct.delete(self.image_positions[position]['id'])
                del self.image_positions[position]
            else:
                # Place the latest rotated image on the grid
                latest_thumbnail = self.image_thumbnails[-1]
                image_id = self.canvas_pct.create_image(x, y, anchor="nw", image=latest_thumbnail)
                self.image_positions[f"{x},{y}"] = {
                    'id': image_id,
                    'rotation': self.rotation_angle,
                    'file_path': self.image_file_path  # Save file path in position data
                }

    def save_positions(self):
        """Saves the current image positions, rotations, and file paths to a JSON file."""
        if self.pn_var_pct.get() == "":
            messagebox.showwarning("Need Part Number", "A part number is needed to save positions")
            return
        halfway = int((self.x_y_grid_count)*self.grid_size/2) if self.x_y_grid_count%2 == 0 else int((self.x_y_grid_count-1)*self.grid_size/2)
        save_data = {
            self.pn_var_pct.get(): {position: {"rotation": info["rotation"], "file_path": info["file_path"], "grid_size": self.x_y_grid_count, 'mirrored': mirror_coordinates(position.split(',')[0], position.split(',')[1], halfway, self.x_y_grid_count, self.grid_size)}
                                    for position, info in self.image_positions.items()}
        }
        save_file = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[("JSON", "*.json")], initialfile=f"{self.pn_var_pct.get()}")
        with open(f"{save_file}", "w") as f:
            json.dump(save_data, f)
        messagebox.showinfo("Saved", "Image positions and file paths saved successfully.")

        database.add_part(self.db_session, self.pn_var_pct.get(), str(list(save_data[self.pn_var_pct.get()].keys())), str(self.pn_layers),)

    def load_positions_pct(self):
        """Loads image positions, rotations, and file paths from a JSON file."""

        # TODO: Add mirroring if layer is even
        try:
            load_file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            with open(load_file, "r") as f:
                loaded_data = json.load(f)
            pn = list(loaded_data.keys())[0]
            self.x_y_grid_count = list(loaded_data[pn].items())[0][1]['grid_size']
            self.redraw_grid(self.canvas_pct)
            for position_str, data in loaded_data[pn].items():
                x, y = map(int, position_str.split(','))
                rotation = data["rotation"]
                file_path = data["file_path"]

                # Verify file exists before loading
                if os.path.exists(file_path):
                    loaded_image = Image.open(file_path)
                    rotated_image = loaded_image.rotate(rotation, expand=True).resize((self.grid_size, self.grid_size))
                    thumbnail = ImageTk.PhotoImage(rotated_image)
                    image_id = self.canvas_pct.create_image(x, y, anchor="nw", image=thumbnail)
                    self.image_thumbnails.append(thumbnail)  # Keep a reference
                    self.image_positions[position_str] = {
                        'id': image_id,
                        'rotation': rotation,
                        'file_path': file_path
                    }
                else:
                    messagebox.showwarning("Warning", f"File '{file_path}' not found.")
            messagebox.showinfo("Loaded", "Image positions loaded successfully.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No saved positions found.")

    # Image Defect Maps
    def create_image_defects_tab(self):
        """Initialize content for the 'Image Defects Map' tab."""
        self.image_defects_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.image_defects_tab, text="Image Defects Map")
        # Grid Canvas
        self.canvas_idt = tk.Canvas(self.image_defects_tab, width=500, height=500, bg="white")
        self.canvas_idt.grid(row=6, column=1, pady=20)
        self.canvas_idt.bind("<Button-1>", self.x_out_images)

        self.draw_grid(self.canvas_idt)

        # Shop Order Number
        tk.Label(self.image_defects_tab, text="Shop Order Number").grid(row=0, column=0, padx=5, pady=5)
        entry_shop_order = tk.Entry(self.image_defects_tab, textvariable=self.shop_order_num_var)
        entry_shop_order.grid(row=0, column=1, padx=5, pady=5)

        # Panel Number
        tk.Label(self.image_defects_tab, text="Panel Number").grid(row=1, column=0, padx=5, pady=5)
        entry_panel_number = tk.Entry(self.image_defects_tab, textvariable=self.panel_num_var)
        entry_panel_number.grid(row=1, column=1, padx=5, pady=5)

        # Part Number
        tk.Label(self.image_defects_tab, text="Part Number").grid(row=0, column=2, padx=5, pady=5)
        entry_part_number = tk.Entry(self.image_defects_tab, textvariable=self.pn_var_idt, state="disabled")
        entry_part_number.grid(row=0, column=3, padx=5, pady=5)



        # Layer Number
        tk.Label(self.image_defects_tab, text="Layer Number").grid(row=1, column=2, padx=5, pady=5)
        self.entry_layer_number = tk.ttk.Combobox(self.image_defects_tab, textvariable=self.layer_num_var, state='readonly', values=[])
        self.entry_layer_number.bind("<<ComboboxSelected>>", self.check_if_inner_layer)
        self.entry_layer_number.grid(row=1, column=3, padx=5, pady=5)

        #
        self.reverse_side_checkbtn = tk.Checkbutton(self.image_defects_tab, text="Reverse", variable=self.reverse_side_var, command=self.flip_side)
        self.reverse_side_checkbtn.grid(row=3, column = 3)

        # Load Panel Layout
        load = tk.Button(self.image_defects_tab, text="Load Panel Layout", command=self.load_positions_idt)
        load.grid(row=3, column=1)

        # Upload to Database
        upload = tk.Button(self.image_defects_tab, text="Insert Data", command=self.load_to_db)
        upload.grid(row=7, column=1, pady=10)

    def reset_idt(self):
        self.image_label.config(image="")
        self.image_thumbnails = []
        self.image_positions = {}
        self.redraw_grid(self.canvas_pct)
        self.increase_grid_button.config(state=tk.ACTIVE)
        self.decrease_grid_button.config(state=tk.ACTIVE)
        return

    def check_if_inner_layer(self, event):
        if self.entry_layer_number['values'][0] == self.layer_num_var.get() or self.entry_layer_number['values'][-1] == self.layer_num_var.get():
            if self.reverse_side_var.get() == 1:
                self.reverse_side_var.set(0)
                self.flip_side()
            else:
                self.reverse_side_var.set(0)

            self.reverse_side_checkbtn.config(state=tk.DISABLED)


        else:
            self.reverse_side_checkbtn.config(state=tk.ACTIVE)


    def flip_side(self):
        self.load_positions_idt(bool(self.reverse_side_var.get()), flip=True)

        return

    def load_positions_idt(self, reverse=False, flip=False):
        try:
            if not flip:
                self.load_file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
                with open(self.load_file, "r") as f:
                    self.loaded_data = json.load(f)
            # Get the Part Number from the JSON File
            pn = list(self.loaded_data.keys())[0]
            self.pn_var_idt.set(pn)
            # Get the layer names
            layer_names = ast.literal_eval(self.db_session.query(database.Part).filter_by(PartNumber=pn).first().LayerNames.strip())
            self.entry_layer_number['values'] = layer_names
            self.x_y_grid_count = list(self.loaded_data[pn].items())[0][1]['grid_size']
            self.redraw_grid(self.canvas_idt, reverse=reverse)
            for position_str, data in self.loaded_data[pn].items():
                if self.reverse_side_var.get(): # If the reverse button is checked Input the reverse coordinates
                    x, y = map(int, self.loaded_data[pn][position_str]['mirrored'].split(','))

                else:
                    x, y = map(int, position_str.split(','))
                rotation = data["rotation"]
                file_path = data["file_path"]

                # Verify file exists before loading
                if os.path.exists(file_path):
                    loaded_image = Image.open(file_path)
                    rotated_image = loaded_image.rotate(rotation, expand=True).resize((self.grid_size, self.grid_size))
                    thumbnail = ImageTk.PhotoImage(rotated_image)
                    image_id = self.canvas_idt.create_image(x, y, anchor="nw", image=thumbnail)
                    self.image_thumbnails.append(thumbnail)  # Keep a reference
                    self.image_positions[position_str] = {
                        'x': False,
                        'line_id1': None,
                        'line_id2': None,

                        'id': image_id,
                        'rotation': rotation,
                        'file_path': file_path,
                        'mirror': f"{x},{y}"
                    }
                else:
                    messagebox.showwarning("Warning", f"File '{file_path}' not found.")
                    return
            if not flip:
                messagebox.showinfo("Loaded", "Image positions loaded successfully.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No saved positions found.")
        return

    def x_out_images(self, event):
        #TODO: SImplify items in the if elif. They can be combined
        grid_size = self.grid_size
        x = (event.x // grid_size) * grid_size
        y = (event.y // grid_size) * grid_size
        position = f"{x},{y}"
        primary_pos = next(iter([ky for ky, value in self.image_positions.items() if value['mirror'] == f'{x},{y}']), None)
        mirrors = [value['mirror'] for ky, value in self.image_positions.items()]
        if position in self.image_positions and not self.reverse_side_var.get():
            if self.image_positions[position]["x"]:
                self.image_positions[position]["x"] = False
                self.canvas_idt.delete(self.image_positions[position]["line_id1"])
                self.canvas_idt.delete(self.image_positions[position]["line_id2"])
                self.image_positions[position]["line_id1"] = None
                self.image_positions[position]["line_id2"] = None
            else:
                self.image_positions[position]["line_id1"] = self.canvas_idt.create_line(x, y, x + self.grid_size, y + self.grid_size, fill="red", width=2)
                self.image_positions[position]["line_id2"] = self.canvas_idt.create_line(x + self.grid_size, y, x, y + self.grid_size, fill="red", width=2)
                self.image_positions[position]["x"] = True
        elif self.reverse_side_var.get() and position in mirrors:
            if self.image_positions[primary_pos]["x"]:
                self.image_positions[primary_pos]["x"] = False
                self.canvas_idt.delete(self.image_positions[primary_pos]["line_id1"])
                self.canvas_idt.delete(self.image_positions[primary_pos]["line_id2"])
                self.image_positions[primary_pos]["line_id1"] = None
                self.image_positions[primary_pos]["line_id2"] = None
            else:
                self.image_positions[primary_pos]["line_id1"] = self.canvas_idt.create_line(x, y, x + self.grid_size, y + self.grid_size, fill="red", width=2)
                self.image_positions[primary_pos]["line_id2"] = self.canvas_idt.create_line(x + self.grid_size, y, x, y + self.grid_size, fill="red", width=2)
                self.image_positions[primary_pos]["x"] = True
            pass
        return


    def check_side(self):
        """
        Check if it is the top or bottom side or if the reverse button is disabled return external
        :return:
        """
        if self.reverse_side_checkbtn['state'] == 'active' or self.reverse_side_checkbtn['state'] == 'normal':
            if self.reverse_side_var.get():
                return 'bottom'
            else:
                return 'top'
        if self.reverse_side_checkbtn['state'] == 'disabled':
            return 'external'

    def load_to_db(self):
        if self.shop_order_num_var.get() == "" or self.layer_num_var.get() == "" or self.pn_var_idt.get() == "" or self.panel_num_var.get() == "":  # Ensure all inputs are met if not throw message error
            messagebox.showwarning("Inputs Needed", "All inputs are necessary to load to the database")
            return
        layer_order = ast.literal_eval(self.db_session.query(database.Part).filter_by(PartNumber=self.pn_var_idt.get()).first().LayerOrder.strip()) # Get the layer names from the database for the pn
        old_list = ["O" for i in layer_order] # Create list of all good parts

        for idx, loc in enumerate(layer_order): # Locate bad parts and replace them in the list
            if self.image_positions[loc]['x']:
                old_list[idx] = "X"
        try:

            side = self.check_side()
            database.add_shop_order_side(self.db_session, self.shop_order_num_var.get(),
                                    self.pn_var_idt.get(), self.layer_num_var.get(), self.panel_num_var.get(),
                                    str(old_list), side)  # Add to database

        except sqlalchemy.exc.IntegrityError as error:
            print(error)
            messagebox.showwarning('Exists in the database', 'This combination of ShopOrder, PartNumber, LayerNumber, PanelNumber exists in the database.')
            self.db_session.close()
            self.create_session()
            self.check_sides_match()  # See if we can combine a front and back layer

            return


        self.check_sides_match() # See if we can combine a front and back layer
        save_data = {
            self.pn_var_idt.get(): {position: {"rotation": info["rotation"], "file_path": info["file_path"]}
                                    for position, info in self.image_positions.items()}
        }
        with open("image_positions.json", "w") as f:
            json.dump(save_data, f)
        messagebox.showinfo("Saved", "Image positions and file paths saved successfully.")

    def check_sides_match(self):
        # Gert matches
        matches = self.db_session.query(database.ShopOrderSides).filter_by(ShopOrderNumber=self.shop_order_num_var.get(), PartNumber=self.pn_var_idt.get(), LayerNumber=self.layer_num_var.get(), PanelNumber=self.panel_num_var.get()).all()

        # Check to see if it is an exernal layer
        if len(matches) == 1 and matches[0].Side == 'external':
            database.add_shop_order(self.db_session, shop_order_number=self.shop_order_num_var.get(),
                                    part_number=self.pn_var_idt.get(), layer_number=self.layer_num_var.get(),
                                    panel_number=self.panel_num_var.get(), images=matches[0].Images)
            self.db_session.delete(matches[0])
            self.db_session.commit()
            return

        # Ensure Only Two Entries for middle layer
        if len(matches) == 2:
            pass
        elif len(matches) > 2:
            messagebox.showerror("Databse Issue", f"There should be a maximum of two entries for middle cores.\n"
                                                  f"Shop Order Number: {self.shop_order_num_var.get()}\n"
                                                  f"Part Number: {self.pn_var_idt.get()}\n"
                                                  f"Panel Number: {self.panel_num_var.get()}\n"
                                                  f"Layer Number: {self.layer_num_var.get()}\n"
                                                  f"has {len(matches)} entries. Please have an administrator delete these entries and re-enter the layer information.")
            return

        if len(matches) < 2:
            return
        count = []
        #Ensure the sides are top bottom
        for side in matches:
            if side.Side == "top":
                count.append("top")
            if side.Side == "bottom":
                count.append("bottom")
        # Assisted by watsonx Code Assistant
        top = ast.literal_eval(self.db_session.query(database.ShopOrderSides).filter_by(ShopOrderNumber=self.shop_order_num_var.get(), LayerNumber=self.layer_num_var.get(), PanelNumber=self.panel_num_var.get(), Side="top").first().Images.strip())
        bottom = ast.literal_eval(self.db_session.query(database.ShopOrderSides).filter_by(ShopOrderNumber=self.shop_order_num_var.get(), LayerNumber=self.layer_num_var.get(), PanelNumber=self.panel_num_var.get(), Side="bottom").first().Images.strip())

        def merge_lists(list1, list2):
            merged_list = []
            for i in range(len(list1)):
                if (list1[i] == 'X' and list2[i] == 'O') or (list1[i] == 'O' and list2[i] == 'X'):
                    merged_list.append('X')
                elif list1[i] == 'O' and list2[i] == 'O':
                    merged_list.append('O')
                else:
                    merged_list.append(list1[i])
            return merged_list

        merged_list = str(merge_lists(top, bottom))

        if "top" in count and "bottom" in count:
            try:
                database.add_shop_order(self.db_session, shop_order_number=self.shop_order_num_var.get(),
                                    part_number=self.pn_var_idt.get(), layer_number=self.layer_num_var.get(),
                                    panel_number=self.panel_num_var.get(), images=merged_list)
                messagebox.showinfo('Success', f'Core {self.layer_num_var.get()} added to matching database successfully.')
                for side in matches:
                    self.db_session.delete(side)
                    self.db_session.commit()
            except Exception as error:
                messagebox.showerror('Error', f'An error occurred while merging information. Please check the error logs. {error}')



if __name__ == "__main__":
    root = tk.Tk()
    app = DefectMatchingApplication(root)
    root.mainloop()
