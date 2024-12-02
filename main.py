import tkinter as tk
from interface.primary_interface import DefectMatchingApplication
import database as db
if __name__ == "__main__":
    db.create_db()
    root = tk.Tk()
    app = DefectMatchingApplication(root)
    root.mainloop()