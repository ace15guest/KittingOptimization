import tkinter as tk
from interface.primary_interface import DefectMatchingApplication
import database as db
import customtkinter as ctk
if __name__ == "__main__":
    db.create_db()
    root = ctk.CTk()
    app = DefectMatchingApplication(root)
    # OptimizationApplication(root)
    root.mainloop()