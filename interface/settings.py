# Assisted by watsonx Code Assistant
import tkinter.filedialog
from tkinter import messagebox
import database
from global_vars.vars import ini_global_path, db_name
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton

class SettingsWindow:
    def __init__(self, ctk_root_top_level:ctk.CTkToplevel):
        self.window = ctk_root_top_level
        self.window.attributes('-topmost', True)
        self.window.grab_set()
        self.window.title("Settings")
        self.window.geometry("650x250")

        # variables
        self.db_entry_var = ctk.StringVar()
        self.ini_entry_var = ctk.StringVar()
        import configparser
        self.config = configparser.ConfigParser()
        self.config.read(ini_global_path)
        self.build_window()



    def build_window(self):

        path = CTkLabel(self.window, text="Database Path: ").grid(row=0, column=0)

        self.db_path_entry = CTkEntry(self.window,width=400, textvariable=self.db_entry_var, state='readonly')
        self.db_path_entry.grid(row=0, column=1)
        self.db_entry_var.set(self.config["DATABASE"]["path"])

        self.db_path_btn = CTkButton(self.window, text="Select Database Path", command=self.select_db_path)
        self.db_path_btn.grid(row=0, column=2, pady=20)

        self.save_button = CTkButton(self.window, text="Save", command=self.save_button_clicked)
        self.save_button.grid(row=2, column=1)
    def select_db_path(self):
        file = tkinter.filedialog.askdirectory(parent=self.window)
        if file == "":
            return
        self.db_entry_var.set(f"{file}/{db_name}")
        self.window.update_idletasks()

    def save_button_clicked(self):


        self.config["DATABASE"]["path"] = self.db_path_entry.get()
        with open(ini_global_path, 'w') as cf:
            self.config.write(cf)
        try:
            database.create_db()
            messagebox.showinfo('Success','Successfully saved the database path. Please Restart the application.')
        except Exception as error:
            print(error)


# custom_window = CustomWindow(ctk.CTkToplevel())
# custom_window.window.mainloop()
