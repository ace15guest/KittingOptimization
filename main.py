import tkinter as tk
from interface.primary_interface import DefectMatchingApplication

if __name__ == "__main__":
    root = tk.Tk()
    app = DefectMatchingApplication(root)
    root.mainloop()