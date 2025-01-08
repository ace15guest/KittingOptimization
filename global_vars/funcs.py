from pathlib import Path
import interface.settings
import customtkinter as ctk

def create_folders(file_path:str):
    # Split the file path into a list of folders
    file_path = file_path.replace('\\','/').replace('//', '/')
    folders = file_path.split('/')

    # Create the folders if they do not exist
    file = Path(file_path)
    file.parent.mkdir(parents=True, exist_ok=True)

def open_settings_window():
    interface.settings.SettingsWindow(ctk.CTkToplevel())