import os

from sqlalchemy import create_engine, Column, String, Integer, DateTime, select
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, PrimaryKeyConstraint, Date
import sqlalchemy
import settings_lib
import datetime
import configparser
import global_vars.vars
import global_vars.funcs


config = configparser.ConfigParser()
config.read(global_vars.vars.ini_global_path)

try:
    db_path = config["DATABASE"]["path"]
    global_vars.funcs.create_folders(db_path)
except KeyError:
    settings_lib.create_config_parser()
    config = configparser.ConfigParser()

    config.read(global_vars.vars.ini_global_path)

    db_path = config["DATABASE"]["path"]
    global_vars.funcs.create_folders(db_path)


except FileNotFoundError:

    settings_lib.create_config_parser()
    config = configparser.ConfigParser()

    config.read(global_vars.vars.ini_global_path)

    db_path = config["DATABASE"]["path"]
    global_vars.funcs.create_folders(db_path)




# Define the database engine and base
engine = create_engine(rf"sqlite:///{db_path}")  # Fixed file path
Base = sqlalchemy.orm.declarative_base()

# Define the ShopOrder model
class ShopOrder(Base):
    __tablename__ = 'shop_orders'

    ShopOrderNumber = Column(String, nullable=False)
    PartNumber = Column(String, nullable=False)
    LayerNumber = Column(String, nullable=False)
    PanelNumber = Column(String, nullable=False)
    Images = Column(String, nullable=False)
    OrderDate = Column(Date, nullable=False, default=datetime.date.today())

    # Composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('ShopOrderNumber', 'PartNumber', 'LayerNumber', 'PanelNumber'),
    )

    def __repr__(self):
        return f"<ShopOrder(ShopOrderNumber={self.ShopOrderNumber}, PartNumber={self.PartNumber}, LayerNumber={self.LayerNumber}, PanelNumber={self.PanelNumber})>"
class ShopOrderSides(Base):
    __tablename__ = 'shop_orders_sides'

    ShopOrderNumber = Column(String, nullable=False)
    PartNumber = Column(String, nullable=False)
    LayerNumber = Column(String, nullable=False)
    PanelNumber = Column(String, nullable=False)
    Images = Column(String, nullable=False)
    Side = Column(String, nullable=False)
    OrderDate = Column(Date, nullable=False, default=datetime.date.today())

    # Composite primary key
    __table_args__ = (PrimaryKeyConstraint('ShopOrderNumber', 'PartNumber', 'LayerNumber', 'PanelNumber', 'Side'),)


class Part(Base):
    __tablename__ = 'part'

    PartNumber = Column(String, nullable=False)
    LayerOrder = Column(String, nullable=False)
    LayerNames = Column(String, nullable=False)

    # Relationship to shop orders
    # shop_orders = relationship("ShopOrder", back_populates="part")

    # def __repr__(self):
    #     return f"<Part(PartNumber={self.PartNumber}, LayerOrder={self.LayerOrder}, LayerNames={self.LayerNames})>"
    __table_args__ = (PrimaryKeyConstraint('PartNumber', 'LayerOrder', 'LayerNames'),)

def add_part(session, part_number, layer_order, layer_names):
    new_part = Part(PartNumber=part_number, LayerOrder=layer_order, LayerNames=layer_names)
    session.add(new_part)
    session.commit()
    print(f"Added part: {new_part}")

def add_shop_order_side(session, shop_order_number, part_number, layer_number, panel_number, images,side):
    new_order = ShopOrderSides(
        ShopOrderNumber=shop_order_number,
        PartNumber=part_number,
        LayerNumber=layer_number,
        PanelNumber=panel_number,
        Images=images,
        Side=side
    )
    session.add(new_order)
    session.commit()


def add_shop_order(session, shop_order_number, part_number, layer_number, panel_number, images):
    new_order = ShopOrder(
        ShopOrderNumber=shop_order_number,
        PartNumber=part_number,
        LayerNumber=layer_number,
        PanelNumber=panel_number,
        Images=images
    )
    session.add(new_order)
    session.commit()


# Create the database and table
def create_db():
    Base.metadata.create_all(engine)


# Usage
if __name__ == "__main__":
    # Create the database and tables
    create_db()
