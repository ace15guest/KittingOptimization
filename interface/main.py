import sqlite3
import tkinter as tk
from tkinter import messagebox

# Function to insert data into the database
def insert_data():
    shop_order = entry_shop_order.get()
    part_number = entry_part_number.get()
    layer_number = entry_layer_number.get()
    panel_number = entry_panel_number.get()
    image_correction = entry_image_correction.get()

    # Check for empty fields
    if not all([shop_order, part_number, layer_number, panel_number, image_correction]):
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    # Insert data into the database
    try:
        with sqlite3.connect(r'C:\Users\Asa Guest\PycharmProjects\KittingOptimization\database\shop_orders.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO shop_orders (ShopOrderNumber, PartNumber, LayerNumber, PanelNumber, Images)
                VALUES (?, ?, ?, ?, ?)
            ''', (shop_order, part_number, layer_number, panel_number, image_correction))
            conn.commit()
            messagebox.showinfo("Success", "Data inserted successfully!")
            clear_entries()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Shop Order Number must be unique.")

# Function to clear input fields
def clear_entries():
    entry_shop_order.delete(0, tk.END)
    entry_part_number.delete(0, tk.END)
    entry_layer_number.delete(0, tk.END)
    entry_panel_number.delete(0, tk.END)
    entry_image_correction.delete(0, tk.END)

# Set up the main application window
root = tk.Tk()
root.title("Shop Order Entry Form")

# Labels and Entry widgets
tk.Label(root, text="Shop Order Number").grid(row=0, column=0, padx=5, pady=5)
entry_shop_order = tk.Entry(root)
entry_shop_order.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Part Number").grid(row=0, column=2, padx=5, pady=5)
entry_part_number = tk.Entry(root)
entry_part_number.grid(row=0, column=3, padx=5, pady=5)

tk.Label(root, text="Layer Number").grid(row=0, column=4, padx=5, pady=5)
entry_layer_number = tk.Entry(root)
entry_layer_number.grid(row=0, column=5, padx=5, pady=5)

tk.Label(root, text="Panel Number").grid(row=0, column=6, padx=5, pady=5)
entry_panel_number = tk.Entry(root)
entry_panel_number.grid(row=0, column=7, padx=5, pady=5)

tk.Label(root, text="Image Correction").grid(row=0, column=8, padx=5, pady=5)
entry_image_correction = tk.Entry(root)
entry_image_correction.grid(row=0, column=9, padx=5, pady=5)

# Buttons
insert_button = tk.Button(root, text="Insert Data", command=insert_data)
insert_button.grid(row=1, column=4, pady=10)

clear_button = tk.Button(root, text="Clear", command=clear_entries)
clear_button.grid(row=1, column=5, pady=10)

# Run the application
root.mainloop()
