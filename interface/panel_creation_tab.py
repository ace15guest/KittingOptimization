#Image imports
from PIL import Image, ImageTk
# GUI imports
import customtkinter as ctk
from tkinter import filedialog, messagebox
#File Imports
import json
import os
import tkinter
# Database Imports
import database
from interface import mirror_coordinates
#
import global_vars.vars
import global_vars.funcs
import settings_lib
class PanelCreationApplication:
    def __init__(self, root):

        self.root = root
        self.window_width = 850
        self.window_height = 800
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.title("Panel Creation")

        ctk.set_appearance_mode("dark")
        # X and Y location variables
        self.x = 0
        self.y = 0

        # Create the database and ini file
        # ini_file_dir = global_vars.vars.ini_global_path
        # settings_lib.create_config_parser(ini_file_dir)
        # Database

        database.create_db()
        Session = database.sessionmaker(bind=database.engine)
        self.db_session = Session()
        # Grid Size
        self.x_y_grid_count = 10
        self.canvas_size = 500
        self.grid_size = int(self.canvas_size/self.x_y_grid_count)

        # Tkinter Variables
        self.pn_var = ctk.StringVar()
        self.layer_name_var = ctk.StringVar()
        self.pn_layers_var = ctk.StringVar()
        # Initialize Variables
        self.image_thumbnails = [] # List to hold rotated thumbnails
        self.image_positions = {}  # Store image placements on the grid with rotation info
        self.pn_layers = []  # Holds layers for storing in database
        # Build the interface
        self.create_interface()

        self.root.mainloop()

    def add_core(self):
        if self.layer_name_entry.get().strip() == "":
            return
        if self.layer_name_entry.get() in self.pn_layers:
            messagebox.showerror('Duplicate', "A duplicate core has been entered. Please enter a unique core name.")
            return
        if ',' in self.layer_name_entry.get():
            messagebox.showerror('Core Name Error', "Please avoid using commas in the core naming convention.")
            return

        self.pn_layers.append(self.layer_name_entry.get())
        self.layer_names_entry.configure(state=ctk.NORMAL)
        self.layer_names_entry.delete(0, ctk.END)

        self.layer_names_entry.insert(0, str(', '.join(self.pn_layers)))
        self.layer_names_entry.configure(state=ctk.DISABLED)
        self.layer_name_var.set("")

    def delete_core(self):
        self.pn_layers = self.pn_layers[0:-1]
        self.layer_names_entry.configure(state=ctk.NORMAL)

        self.layer_names_entry.delete(0, ctk.END)

        self.layer_names_entry.insert(0, str(', '.join(self.pn_layers)))
        self.layer_names_entry.configure(state=ctk.DISABLED)

    def create_interface(self):
        # Part Number Entry
        self.x += self.window_width/7
        part_number_label = ctk.CTkLabel(self.root, text="Part Number:")
        part_number_label.place(x=self.x, y=self.y)
        self.x += 75
        self.part_number_entry = ctk.CTkEntry(self.root, textvariable=self.pn_var)
        self.part_number_entry.place(x=self.x, y=self.y)

        # Adding and Removing Layers
        self.add_button = ctk.CTkButton(self.root, text="Add Core", command=self.add_core)
        self.add_button.place(x=self.x+200, y=self.y)
        self.remove_button = ctk.CTkButton(self.root, text="Remove Core", command=self.delete_core)
        self.remove_button.place(x=self.x+340, y=self.y)
        self.layer_name_entry = ctk.CTkEntry(self.root, textvariable=self.layer_name_var)
        self.layer_name_entry.place(x=self.x+480, y=self.y)

        self.y+=40
        self.layer_names_entry = ctk.CTkEntry(self.root, textvariable=self.pn_layers_var, width=420, state=ctk.DISABLED)
        self.layer_names_entry.place(x=self.x + 200, y=self.y)
        # Upload an Image
        upload_button = ctk.CTkButton(self.root, text="Upload Image", command=self.upload_image)
        upload_button.place(x=self.x, y=self.y)
        self.x +=20
        self.y +=30

        self.image_label = ctk.CTkLabel(self.root, text=None)
        self.image_label.place(x=self.x, y=self.y,)
        self.x-=25
        self.y+=90
        rotate_button = ctk.CTkButton(self.root, text="Rotate Image 90°", command=self.rotate_image)
        rotate_button.place(x=self.x, y =self.y)

        self.x = 0
        self.y+=60

        # Build grid Buttons
        self.increase_grid_button = ctk.CTkButton(self.root, text="Increase Grid Number", command=self.increase_grid)
        self.increase_grid_button.place(x=self.x, y= self.y)
        self.x+=365/2
        self.reset_idt_button = ctk.CTkButton(self.root, text="Reset", command=self.reset_idt)
        self.reset_idt_button.place(x=self.x, y=self.y)
        self.x+=365/2

        self.decrease_grid_button = ctk.CTkButton(self.root, text="Decrease Grid Number", command=self.decrease_grid)
        self.decrease_grid_button.place(x=self.x, y= self.y)
        self.y+=30

        # Save and Load Buttons
        save_button = ctk.CTkButton(self.root, text="Save Positions", command=self.save_positions)
        save_button.place(x=self.x+140, y=self.y+160)
        load_button = ctk.CTkButton(self.root, text="Load Positions", command=self.load_positions_pct)
        load_button.place(x=self.x+140, y=self.y+210)

        self.x=0
        self.build_canvas()
        # Menu Bar
        menubar = tkinter.Menu(self.root)
        self.root.configure(menu=menubar)

        settings_menu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Edit', menu=settings_menu)

        settings_menu.add_command(label="Settings", command=global_vars.funcs.open_settings_window)
        pass
    def rotate_image(self):
        """Rotates the loaded image by 90 degrees."""
        if self.loaded_image:
            self.rotation_angle = (self.rotation_angle + 90) % 360
            self.apply_rotation()
        else:
            messagebox.showwarning("Warning", "No image uploaded to rotate.")

    def upload_image(self):
        """Handles uploading an image and prepares it for display."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp")])
        if file_path:
            self.image_file_path = file_path
            self.loaded_image = Image.open(self.image_file_path)
            self.rotation_angle = 0  # Reset rotation on new image
            self.apply_rotation()
            self.increase_grid_button.configure(state=ctk.DISABLED)
            self.decrease_grid_button.configure(state=ctk.DISABLED)

    def apply_rotation(self):
        """Applies the current rotation to the loaded image and updates the display."""
        if self.loaded_image:
            orig_img = self.loaded_image.rotate(self.rotation_angle, expand=True).resize((100,100))
            rotated_image = self.loaded_image.rotate(self.rotation_angle, expand=True).resize((self.grid_size, self.grid_size))
            thumbnail = ImageTk.PhotoImage(rotated_image)
            view_thumbnail = ImageTk.PhotoImage(orig_img, size=(50,50))
            self.image_thumbnails.append(thumbnail)  # Store each rotated instance
            self.image_label.configure(image=view_thumbnail)
            self.image_label.image = thumbnail  # Keep a reference to avoid garbage collection

    def reset_idt(self):
        self.image_label.configure(image="")
        self.image_thumbnails = []
        self.image_positions = {}
        self.image_file_path = ""
        self.loaded_image = None
        self.redraw_grid(self.canvas)
        self.increase_grid_button.configure(state=ctk.ACTIVE)
        self.decrease_grid_button.configure(state=ctk.ACTIVE)
        return

    def build_canvas(self):
        # Create the canvas
        self.canvas = ctk.CTkCanvas(self.root, width= self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.place(x=self.x, y=self.y)

        self.canvas.bind("<Button-1>", self.place_image_on_grid)

        self.draw_grid(self.canvas)
        pass
    def redraw_grid(self, canvas, reverse=False):
        self.grid_size = int(500 / self.x_y_grid_count)
        self.canvas_size = self.grid_size * self.x_y_grid_count
        canvas.config(height=self.canvas_size, width=self.canvas_size)
        color = 'gray'
        if reverse:
            color = 'red'
        self.draw_grid(canvas, color=color)
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
                self.canvas.delete(self.image_positions[position]['id'])
                del self.image_positions[position]
            else:
                # Place the latest rotated image on the grid
                latest_thumbnail = self.image_thumbnails[-1]
                image_id = self.canvas.create_image(x, y, anchor="nw", image=latest_thumbnail)
                self.image_positions[f"{x},{y}"] = {
                    'id': image_id,
                    'rotation': self.rotation_angle,
                    'file_path': self.image_file_path  # Save file path in position data
                }
    def increase_grid(self):
        if self.x_y_grid_count >= 20:
            messagebox.showerror('Max Grid Reached', 'A 20 x 20 grid is the largest possible grid size')
            return
        self.x_y_grid_count+=1

        self.grid_size = int(500/self.x_y_grid_count)
        self.canvas_size = self.grid_size*self.x_y_grid_count
        self.canvas.config(height=self.canvas_size, width=self.canvas_size)

        self.draw_grid(self.canvas)

    def decrease_grid(self):
        if self.x_y_grid_count <= 2:
            messagebox.showerror('Min Grid Reached', 'A 2 x 2 grid is the smallest possible grid size')
            return
        self.x_y_grid_count -= 1
        self.grid_size = int(500 / self.x_y_grid_count)
        self.canvas_size = self.grid_size*self.x_y_grid_count
        self.canvas.config(height=self.canvas_size, width=self.canvas_size)

        self.draw_grid(self.canvas)

    def save_positions(self):
        """Saves the current image positions, rotations, and file paths to a JSON file."""
        if self.pn_var.get() == "":
            messagebox.showwarning("Need Part Number", "A part number is needed to save positions")
            return
        if len(self.pn_layers) < 2:
            messagebox.showwarning("Core Error", "Please insert 2 cores or more")
            return
        halfway = int((self.x_y_grid_count)*self.grid_size/2) if self.x_y_grid_count%2 == 0 else int((self.x_y_grid_count-1)*self.grid_size/2)
        save_data = {
            self.pn_var.get(): {position: {"rotation": info["rotation"], "file_path": info["file_path"], "grid_size": self.x_y_grid_count, 'mirrored': mirror_coordinates(position.split(',')[0], position.split(',')[1], halfway, self.x_y_grid_count, self.grid_size)}
                                    for position, info in self.image_positions.items()}
        }
        save_file = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[("JSON", "*.json")], initialfile=f"{self.pn_var.get()}")
        with open(f"{save_file}", "w") as f:
            json.dump(save_data, f)
        messagebox.showinfo("Saved", "Image positions and file paths saved successfully.")

        database.add_part(self.db_session, self.pn_var.get(), str(list(save_data[self.pn_var.get()].keys())), str(self.pn_layers),)
    def load_positions_pct(self):
        """Loads image positions, rotations, and file paths from a JSON file."""


        try:
            load_file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            with open(load_file, "r") as f:
                loaded_data = json.load(f)
            pn = list(loaded_data.keys())[0]
            self.x_y_grid_count = list(loaded_data[pn].items())[0][1]['grid_size']
            self.redraw_grid(self.canvas)
            for position_str, data in loaded_data[pn].items():
                x, y = map(int, position_str.split(','))
                rotation = data["rotation"]
                file_path = data["file_path"]

                # Verify file exists before loading
                if os.path.exists(file_path):
                    loaded_image = Image.open(file_path)
                    rotated_image = loaded_image.rotate(rotation, expand=True).resize((self.grid_size, self.grid_size))
                    thumbnail = ImageTk.PhotoImage(rotated_image)
                    image_id = self.canvas.create_image(x, y, anchor="nw", image=thumbnail)
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
if __name__ == '__main__':
    root = ctk.CTk()
    PanelCreationApplication(root)