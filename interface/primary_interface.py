import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import sqlalchemy.exc
from PIL import Image, ImageTk
import json
import os
import database
import ast


class DefectMatchingApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel Matching Application")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Initialize variables
        self.db_location = r"C:\Users\Asa Guest\PycharmProjects\KittingOptimization\interface\shop_orders.db"
        self.image_positions = {}  # Store image placements on the grid with rotation info
        self.rotation_angle = 0  # Track the current rotation angle of the image
        self.loaded_image = None  # Original loaded image
        self.image_file_path = None  # Store path of the currently loaded image
        self.image_thumbnails = []  # List to hold rotated thumbnails
        self.pn_layers = [] # Holds layers

        #Database connection
        Session = database.sessionmaker(bind=database.engine)
        self.db_session = Session()

        # Input Vars
        self.pn_var_pct = tk.StringVar()

        self.shop_order_num_var = tk.StringVar()
        self.layer_num_var = tk.StringVar()
        self.pn_var_idt = tk.StringVar()
        self.panel_num_var = tk.StringVar()

        # PCT Vars
        self.layer_name_var = tk.StringVar()
        self.pn_layers_var = tk.StringVar()

        # Set up tabs and widgets
        self.create_panel_creation_tab()
        self.create_image_defects_tab()

    # Panel Creation

    def create_session(self):
        Session = database.sessionmaker(bind=database.engine)
        self.db_session = Session()
    def create_panel_creation_tab(self):
        """Creates the Panel Creation tab and its components."""
        self.panel_creation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.panel_creation_tab, text="Panel Creation")

        # Part Number Entry
        part_label = tk.Label(self.panel_creation_tab, text="Part Number:")
        part_label.grid(row=0, column=1, pady=5)
        self.part_number_entry = tk.Entry(self.panel_creation_tab, textvariable=self.pn_var_pct, width=20)
        self.part_number_entry.grid(row=0, column=2, pady=5)

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

        # Grid Canvas
        self.canvas_pct = tk.Canvas(self.panel_creation_tab, width=500, height=500, bg="white")
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

    def apply_rotation(self):
        """Applies the current rotation to the loaded image and updates the display."""
        if self.loaded_image:
            rotated_image = self.loaded_image.rotate(self.rotation_angle, expand=True).resize((50, 50))
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

    def draw_grid(self, canvas_used):
        """Draws the grid on the canvas_pct."""
        grid_size = 50
        for x in range(0, 500, grid_size):
            canvas_used.create_line(x, 0, x, 500, fill="gray")
        for y in range(0, 500, grid_size):
            canvas_used.create_line(0, y, 500, y, fill="gray")

    def place_image_on_grid(self, event):
        """Places the rotated image thumbnail on the grid without clearing existing placements."""
        if self.image_thumbnails and self.image_file_path:
            grid_size = 50
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
        save_data = {
            self.pn_var_pct.get(): {position: {"rotation": info["rotation"], "file_path": info["file_path"]}
                              for position, info in self.image_positions.items()}
        }
        save_file = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[("JSON", "*.json")], initialfile=f"{self.pn_var_pct.get()}")
        with open(f"{save_file}", "w") as f:
            json.dump(save_data, f)
        messagebox.showinfo("Saved", "Image positions and file paths saved successfully.")

        database.add_part(self.db_session, self.pn_var_pct.get(), str(list(save_data[self.pn_var_pct.get()].keys())), str(self.pn_layers))

    def load_positions_pct(self):
        """Loads image positions, rotations, and file paths from a JSON file."""

        # TODO: Add mirroring if layer is even
        try:
            load_file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            with open(load_file, "r") as f:
                loaded_data = json.load(f)
            pn = list(loaded_data.keys())[0]
            for position_str, data in loaded_data[pn].items():
                x, y = map(int, position_str.split(','))
                rotation = data["rotation"]
                file_path = data["file_path"]

                # Verify file exists before loading
                if os.path.exists(file_path):
                    loaded_image = Image.open(file_path)
                    rotated_image = loaded_image.rotate(rotation, expand=True).resize((50, 50))
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
        self.entry_layer_number.grid(row=1, column=3, padx=5, pady=5)



        # Load Panel Layout
        load = tk.Button(self.image_defects_tab, text="Load Panel Layout", command=self.load_positions_idt)
        load.grid(row=3, column=1)

        # Upload to Database
        upload = tk.Button(self.image_defects_tab, text="Insert Data", command=self.load_to_db)
        upload.grid(row=7, column=1, pady=10)

    def load_positions_idt(self):
        try:
            load_file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            with open(load_file, "r") as f:
                loaded_data = json.load(f)
            pn =list(loaded_data.keys())[0]
            self.pn_var_idt.set(pn)
            layer_names = ast.literal_eval(self.db_session.query(database.Part).filter_by(PartNumber=pn).first().LayerNames.strip())
            self.entry_layer_number['values'] = layer_names
            for position_str, data in loaded_data[pn].items():
                x, y = map(int, position_str.split(','))
                rotation = data["rotation"]
                file_path = data["file_path"]

                # Verify file exists before loading
                if os.path.exists(file_path):
                    loaded_image = Image.open(file_path)
                    rotated_image = loaded_image.rotate(rotation, expand=True).resize((50, 50))
                    thumbnail = ImageTk.PhotoImage(rotated_image)
                    image_id = self.canvas_idt.create_image(x, y, anchor="nw", image=thumbnail)
                    self.image_thumbnails.append(thumbnail)  # Keep a reference
                    self.image_positions[position_str] = {
                        'x': False,
                        'line_id1': None,
                        'line_id2': None,

                        'id': image_id,
                        'rotation': rotation,
                        'file_path': file_path
                    }
                else:
                    messagebox.showwarning("Warning", f"File '{file_path}' not found.")
            messagebox.showinfo("Loaded", "Image positions loaded successfully.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No saved positions found.")
        return

    def x_out_images(self, event):
        grid_size = 50
        x = (event.x // grid_size) * grid_size
        y = (event.y // grid_size) * grid_size
        position = f"{x},{y}"

        if position in self.image_positions:
            if self.image_positions[position]["x"] == True:
                self.image_positions[position]["x"] = False
                self.canvas_idt.delete(self.image_positions[position]["line_id1"])
                self.canvas_idt.delete(self.image_positions[position]["line_id2"])
                self.image_positions[position]["line_id1"] = None
                self.image_positions[position]["line_id2"] = None
            else:
                self.image_positions[position]["line_id1"] = self.canvas_idt.create_line(x, y, x + 50, y + 50, fill="red", width=2)
                self.image_positions[position]["line_id2"] = self.canvas_idt.create_line(x + 50, y, x, y + 50, fill="red", width=2)
                self.image_positions[position]["x"] = True

        return

    def load_to_db(self):
        if self.shop_order_num_var.get() == "" or self.layer_num_var.get() == "" or self.pn_var_idt.get() == "" or self.panel_num_var.get() == "":
            messagebox.showwarning("Inputs Needed", "All inputs are necessary to load to the database")
            return
        layer_order = ast.literal_eval(self.db_session.query(database.Part).filter_by(PartNumber=self.pn_var_idt.get()).first().LayerOrder.strip())
        old_list = ["O" for i in layer_order]

        for idx, loc in enumerate(layer_order):
            if self.image_positions[loc]['x']:
                old_list[idx] = "X"
        try:
            database.add_shop_order(self.db_session, self.shop_order_num_var.get(), self.pn_var_idt.get(), self.layer_num_var.get(), self.panel_num_var.get(), str(old_list))
        except sqlalchemy.exc.IntegrityError:
            messagebox.showwarning('Exists in the database','This combination of ShopOrder, PartNumber, LayerNumber, PanelNumber exists in the database.')
            self.db_session.close()
            self.create_session()
            return

        save_data = {
            self.pn_var_idt.get(): {position: {"rotation": info["rotation"], "file_path": info["file_path"]}
                                    for position, info in self.image_positions.items()}
        }
        with open("image_positions.json", "w") as f:
            json.dump(save_data, f)
        messagebox.showinfo("Saved", "Image positions and file paths saved successfully.")

        return


if __name__ == "__main__":
    root = tk.Tk()
    app = DefectMatchingApplication(root)
    root.mainloop()
