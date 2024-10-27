import sqlite3


def create_db():
    # Connect to the database (or create it)
    connection = sqlite3.connect('shop_orders.db')
    cursor = connection.cursor()

    # Create the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_orders (
            ShopOrderNumber TEXT PRIMARY KEY,
            PartNumber TEXT NOT NULL,
            LayerNumber INTEGER NOT NULL,
            PanelNumber INTEGER NOT NULL,
            Images TEXT NOT NULL
        )
    ''')

    # Commit changes and close the connection
    connection.commit()
    connection.close()

    print("Database and table created successfully.")
