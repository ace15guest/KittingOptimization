import tkinter as tk
from tkinter import ttk


class DualTabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual Tab Interface")

        # Create the notebook (tab container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Create the "Panel Creation" tab
        self.panel_creation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.panel_creation_tab, text="Panel Creation")

        # Create the "Image Defects Map" tab
        self.image_defects_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.image_defects_tab, text="Image Defects Map")

        # Initialize tab contents
        self.create_panel_creation_tab_content()
        self.create_image_defects_tab_content()

    def create_panel_creation_tab_content(self):
        """Initialize content for the 'Panel Creation' tab."""
        label = tk.Label(self.panel_creation_tab, text="Panel Creation Section", font=("Arial", 16))
        label.pack(pady=20)

        # You can add additional widgets for panel creation here

    def create_image_defects_tab_content(self):
        """Initialize content for the 'Image Defects Map' tab."""
        label = tk.Label(self.image_defects_tab, text="Image Defects Map Section", font=("Arial", 16))
        label.pack(pady=20)

        # You can add additional widgets for image defects mapping here


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = DualTabApp(root)
    root.mainloop()
