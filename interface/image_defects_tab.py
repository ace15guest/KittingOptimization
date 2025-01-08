import tkinter

import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
from PIL import Image, ImageTk, ImageOps
import ast
import database
import sqlalchemy
import global_vars
import settings_lib
import interface.settings
import global_vars.vars
import global_vars.funcs




class ImageDefectsApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Defects")

        self.window_width = 920
        self.window_height = 800
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        # Initialize Variables
        self.x_y_grid_count = 10
        self.canvas_size = 500
        self.grid_size = int(self.canvas_size / self.x_y_grid_count)
        self.image_positions = {}
        self.image_thumbnails = []


        # Database
        database.create_db()
        Session = database.sessionmaker(bind=database.engine)
        self.db_session = Session()

        # Ctk Variables
        self.shop_order_num_var = ctk.StringVar() # The variable that will hold the shop order number
        self.panel_num_var = ctk.StringVar() # The variable holding the panel number
        self.pn_var = ctk.StringVar()
        self.reverse_side_var = ctk.IntVar() # Variable keeping track of whether the reverse side is clicked
        self.layer_name_var = ctk.StringVar()
        self.layer_num_var = ctk.StringVar()
        self.opt_menu_var = ctk.StringVar() # Custom Tkinter Option Menu Var




        # Build the interface
        self.create_interface()


        self.root.mainloop()


    def create_interface(self):
        # Create  Canvas

        self.canvas_idt = ctk.CTkCanvas(self.root, width=500, height=500, bg="white")
        self.canvas_idt.grid(row=6, column=1, pady=20)
        self.canvas_idt.bind("<Button-1>", self.x_out_images)

        self.draw_grid(self.canvas_idt)
        # Shop Order Number
        ctk.CTkLabel(self.root, text="Shop Order Number").grid(row=0, column=0, padx=5, pady=5)
        entry_shop_order = ctk.CTkEntry(self.root, textvariable=self.shop_order_num_var)
        entry_shop_order.grid(row=0, column=1, padx=5, pady=5)

        # Layer Number
        ctk.CTkLabel(self.root, text="Layer Number").grid(row=1, column=2, padx=5, pady=5)
        self.entry_layer_number = ctk.CTkComboBox(self.root, variable=self.layer_num_var, values=[], state='readonly', command=self.check_if_inner_layer)

        self.entry_layer_number.grid(row=1, column=3, padx=5, pady=5)

        # Panel Number
        ctk.CTkLabel(self.root, text="Panel Number").grid(row=1, column=0, padx=5, pady=5)
        entry_panel_number = ctk.CTkEntry(self.root, textvariable=self.panel_num_var)
        entry_panel_number.grid(row=1, column=1, padx=5, pady=5)

        # Part Number
        ctk.CTkLabel(self.root, text="Part Number").grid(row=0, column=2, padx=5, pady=5)
        entry_part_number = ctk.CTkEntry(self.root, textvariable=self.pn_var, state="disabled")
        entry_part_number.grid(row=0, column=3, padx=5, pady=5)

        load = ctk.CTkButton(self.root, text="Load Panel Layout", command=self.load_positions_idt)
        load.grid(row=3, column=1)

        #Check Button
        self.reverse_side_checkbtn = ctk.CTkCheckBox(self.root, text="Reverse", variable=self.reverse_side_var, command=self.flip_side)
        self.reverse_side_checkbtn.grid(row=3, column=3)

        # Upload to Database
        upload = ctk.CTkButton(self.root, text="Insert Data", command=self.load_to_db)
        upload.grid(row=7, column=1, pady=10)

        # Menu Bar
        menubar = tkinter.Menu(self.root)
        self.root.configure(menu=menubar)

        settings_menu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label = 'Edit', menu=settings_menu)

        settings_menu.add_command(label="Settings", command=global_vars.funcs.open_settings_window)

    def draw_grid(self, canvas_used, color='gray'):
        """Draws the grid on the canvas_pct."""
        grid_size = self.grid_size
        canvas_used.delete('all')
        for x in range(0, self.canvas_size, grid_size):
            canvas_used.create_line(x, 0, x, 500, fill=color)
        for y in range(0, self.canvas_size, grid_size):
            canvas_used.create_line(0, y, self.canvas_size, y, fill=color)
    def redraw_grid(self, canvas, reverse=False):
        self.grid_size = int(500 / self.x_y_grid_count)
        self.canvas_size = self.grid_size * self.x_y_grid_count
        canvas.config(height=self.canvas_size, width=self.canvas_size)
        color = 'gray'
        if reverse:
            color = 'red'
        self.draw_grid(canvas, color=color)
    def remove_xs_from_images(self):
        grid_size = self.grid_size
        primary_coords = [key for key in self.image_positions.keys()]
        mirrored_coords = [mirror for key in self.image_positions.keys() for mirror in self.image_positions[key]["mirror"]]

        for p_coord in primary_coords:
            self.canvas_idt.delete(self.image_positions[p_coord]["line_id1"])
            self.canvas_idt.delete(self.image_positions[p_coord]["line_id2"])
            self.image_positions[p_coord]["line_id1"] = None
            self.image_positions[p_coord]["line_id2"] = None

    def x_out_images(self, event):
        grid_size = self.grid_size
        x = (event.x // grid_size) * grid_size
        y = (event.y // grid_size) * grid_size
        position = f"{x},{y}"
        primary_pos = next(iter([ky for ky, value in self.image_positions.items() if value['mirror'] == f'{x},{y}']), None)
        mirrors = [value['mirror'] for ky, value in self.image_positions.items()]

        if position in self.image_positions and not self.reverse_side_var.get():
            pass
        elif self.reverse_side_var.get() and position in mirrors:
            position = primary_pos
        if position in self.image_positions or position in mirrors:
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


        return

    def flip_side(self):
        self.load_positions_idt(bool(self.reverse_side_var.get()), flip=True)

        return

    def check_if_inner_layer(self, event):
        if self.entry_layer_number._values[0] == self.layer_num_var.get() or self.entry_layer_number._values[-1] == self.layer_num_var.get():
            if self.reverse_side_var.get() == 1:
                self.reverse_side_var.set(0)
                self.flip_side()
            else:
                self.reverse_side_var.set(0)

            self.reverse_side_checkbtn.configure(state=ctk.DISABLED)
        else:
            self.reverse_side_checkbtn.configure(state=ctk.NORMAL)

    def load_positions_idt(self, reverse=False, flip=False):
        try:
            if not flip:
                self.load_file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
                with open(self.load_file, "r") as f:
                    self.loaded_data = json.load(f)
            if not self.loaded_data:
                return
            # Get the Part Number from the JSON File
            pn = list(self.loaded_data.keys())[0]
            self.pn_var.set(pn)
            # Get the layer names
            layer_names = ast.literal_eval(self.db_session.query(database.Part).filter_by(PartNumber=pn).first().LayerNames.strip())
            self.entry_layer_number.configure(values=layer_names)
            if not flip: # Only need to do this if we are loading a new Part Number in
                self.entry_layer_number.set(layer_names[0])
                self.check_if_inner_layer(None)
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
                    if reverse:
                        rotated_image = ImageOps.mirror(rotated_image)
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

    def load_to_db(self):
        if self.shop_order_num_var.get() == "" or self.layer_num_var.get() == "" or self.pn_var.get() == "" or self.panel_num_var.get() == "":  # Ensure all inputs are met if not throw message error
            messagebox.showwarning("Inputs Needed", "All inputs are necessary to load to the database")
            return
        layer_order = ast.literal_eval(self.db_session.query(database.Part).filter_by(PartNumber=self.pn_var.get()).first().LayerOrder.strip()) # Get the layer names from the database for the pn
        old_list = ["O" for i in layer_order] # Create list of all good parts

        for idx, loc in enumerate(layer_order): # Locate bad parts and replace them in the list
            if self.image_positions[loc]['x']:
                old_list[idx] = "X"
        try:

            side = self.check_side()
            database.add_shop_order_side(self.db_session, self.shop_order_num_var.get(),
                                    self.pn_var.get(), self.layer_num_var.get(), self.panel_num_var.get(),
                                    str(old_list), side)  # Add to database

        except sqlalchemy.exc.IntegrityError as error:
            print(error)
            messagebox.showwarning('Exists in the database', 'This combination of ShopOrder, PartNumber, LayerNumber, PanelNumber exists in the database.')
            self.db_session.close()
            self.create_session()
            self.check_sides_match()  # See if we can combine a front and back layer

            return
        self.remove_xs_from_images()


        self.check_sides_match() # See if we can combine a front and back layer
        save_data = {
            self.pn_var.get(): {position: {"rotation": info["rotation"], "file_path": info["file_path"]}
                                    for position, info in self.image_positions.items()}
        }
        with open("image_positions.json", "w") as f:
            json.dump(save_data, f)
        messagebox.showinfo("Saved", "Image positions and file paths saved successfully.")
        # Clear the panel image
        self.panel_num_var.set("")
    def check_side(self):
        """
        Check if it is the top or bottom side or if the reverse button is disabled return external
        :return:
        """
        if self.reverse_side_checkbtn._state == 'active' or self.reverse_side_checkbtn._state == 'normal':
            if self.reverse_side_var.get():
                return 'bottom'
            else:
                return 'top'
        if self.reverse_side_checkbtn._state == 'disabled':
            return 'external'

    def create_session(self):
        Session = database.sessionmaker(bind=database.engine)
        self.db_session = Session()

    def check_sides_match(self):
        # Gert matches
        matches = self.db_session.query(database.ShopOrderSides).filter_by(ShopOrderNumber=self.shop_order_num_var.get(), PartNumber=self.pn_var.get(), LayerNumber=self.layer_num_var.get(), PanelNumber=self.panel_num_var.get()).all()

        # Check to see if it is an exernal layer
        if len(matches) == 1 and matches[0].Side == 'external':
            database.add_shop_order(self.db_session, shop_order_number=self.shop_order_num_var.get(),
                                    part_number=self.pn_var.get(), layer_number=self.layer_num_var.get(),
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
                                                  f"Part Number: {self.pn_var.get()}\n"
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
                                    part_number=self.pn_var.get(), layer_number=self.layer_num_var.get(),
                                    panel_number=self.panel_num_var.get(), images=merged_list)
                messagebox.showinfo('Success', f'Core {self.layer_num_var.get()} added to matching database successfully.')
                for side in matches:
                    self.db_session.delete(side)
                    self.db_session.commit()
            except Exception as error:
                messagebox.showerror('Error', f'An error occurred while merging information. Please check the error logs. {error}')

