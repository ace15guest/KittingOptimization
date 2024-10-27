import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import shutil
from PIL import Image, ImageTk


class ImageUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Upload Interface")

        self.image = None
        self.image_thumbnail = None
        self.image_positions = {}
        self.image_directory = "saved_images"
        self.current_image_path = None
        self.loaded_images = []
        self.image_loaded = False

        # Initialize interface components
        self.create_part_number_entry()
        self.create_upload_button()
        self.create_image_display_label()
        self.create_save_button()
        self.create_load_button()
        self.create_grid_canvas()

        os.makedirs(self.image_directory, exist_ok=True)

    def create_part_number_entry(self):
        """Creates an entry field to input the part number."""
        part_label = tk.Label(self.root, text="Part Number:")
        part_label.pack(pady=5)

        self.part_number_entry = tk.Entry(self.root, width=20)
        self.part_number_entry.pack(pady=5)

    def create_upload_button(self):
        """Creates an upload button to select and upload an image."""
        self.upload_button = tk.Button(self.root, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=20)

    def create_image_display_label(self):
        """Creates a label for displaying the uploaded image."""
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=20)

    def create_save_button(self):
        """Creates a button to save the grid positions and part numbers."""
        self.save_button = tk.Button(self.root, text="Save Grid Positions", command=self.save_grid_positions)
        self.save_button.pack(pady=20)

    def create_load_button(self):
        """Creates a button to load saved grid positions and images."""
        self.load_button = tk.Button(self.root, text="Load Grid Positions", command=self.load_grid_positions)
        self.load_button.pack(pady=20)

    def create_grid_canvas(self):
        """Creates a canvas_pct area with a grid overlay where the image can be placed."""
        self.canvas = tk.Canvas(self.root, width=500, height=500, bg="white")
        self.canvas.pack(pady=20)

        self.canvas.bind("<Button-1>", self.place_image_on_grid)

        self.draw_grid()

    def draw_grid(self):
        """Draws a grid on the canvas_pct."""
        grid_size = 50
        for x in range(0, 500, grid_size):
            self.canvas.create_line(x, 0, x, 500, fill="gray")
        for y in range(0, 500, grid_size):
            self.canvas.create_line(0, y, 500, y, fill="gray")

    def upload_image(self):
        """Opens a file dialog to upload an image and displays it."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp")])

        if file_path:
            self.display_image(file_path)
            self.image_loaded = True
            self.current_image_path = file_path
            self.prepare_thumbnail(file_path)
        else:
            self.image_loaded = False

    def display_image(self, file_path):
        """Loads the selected image and displays it in the label."""
        try:
            img = Image.open(file_path)
            img = img.resize((250, 250))
            img = ImageTk.PhotoImage(img)

            self.image_label.config(image=img)
            self.image_label.image = img
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.image_loaded = False

    def prepare_thumbnail(self, file_path):
        """Prepares a smaller thumbnail of the image to place on the grid."""
        try:
            img = Image.open(file_path)
            img = img.resize((50, 50))
            self.image_thumbnail = ImageTk.PhotoImage(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create thumbnail: {e}")
            self.image_thumbnail = None

    def place_image_on_grid(self, event):
        """Places the image thumbnail at the nearest grid intersection and stores its location."""
        if self.image_loaded and self.image_thumbnail:
            part_number = self.part_number_entry.get()
            grid_size = 50
            x = (event.x // grid_size) * grid_size
            y = (event.y // grid_size) * grid_size

            img_id = self.canvas.create_image(x, y, anchor="nw", image=self.image_thumbnail)
            self.loaded_images.append(img_id)
            self.image_positions[(x, y)] = {"part_number": part_number, "image_path": self.current_image_path}
            print(f"Placed part number '{part_number}' at position ({x}, {y})")
        else:
            messagebox.showwarning("Warning", "No image loaded. Please upload an image first.")

    def save_grid_positions(self):
        """Saves the grid positions and part numbers to a JSON file."""
        if not self.image_positions:
            print("No images to save.")
            return

        string_image_positions = {
            f"{x},{y}": {"part_number": data["part_number"], "image_path": data["image_path"]}
            for (x, y), data in self.image_positions.items()
        }

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as json_file:
                json.dump(string_image_positions, json_file, indent=4)
            print(f"Grid positions saved to {file_path}")

            for position, data in self.image_positions.items():
                if data["image_path"]:
                    image_name = os.path.basename(data["image_path"])
                    destination = os.path.join(self.image_directory, image_name)
                    shutil.copy(data["image_path"], destination)

            print(f"Images saved to {self.image_directory}")

    def load_grid_positions(self):
        """Loads saved grid positions and associated images from a JSON file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as json_file:
                loaded_positions = json.load(json_file)

            self.canvas.delete("all")
            self.loaded_images.clear()
            self.image_positions.clear()
            self.draw_grid()

            # Load positions and draw X's
            for position, data in loaded_positions.items():
                x, y = map(int, position.split(','))
                part_number = data["part_number"]
                self.canvas.create_text(x + 25, y + 25, text="X", font=("Arial", 24), fill="red")  # Draw X in the center

                # Update the part number entry for display or further use
                self.part_number_entry.delete(0, tk.END)
                self.part_number_entry.insert(0, part_number)

            print("Grid positions loaded and displayed as X's.")


# Initialize the main application
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageUploaderApp(root)
    root.mainloop()
