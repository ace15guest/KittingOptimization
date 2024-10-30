from sqlalchemy import create_engine, Column, String, Integer, DateTime
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
# Define the database engine and base
engine = create_engine(r"sqlite:///C:\Users\6J2739897\Documents\projects\KittingOptimization\Assets\database\shop_orders.db")
Base = sqlalchemy.orm.declarative_base()


# Define the ShopOrder model
class ShopOrder(Base):
    __tablename__ = 'shop_orders'

    ShopOrderNumber = Column(String, primary_key=True)
    PartNumber = Column(String, primary_key=True)
    LayerNumber = Column(String, primary_key=True)
    PanelNumber = Column(String, primary_key=True)
    Images = Column(String, nullable=False)
    # OrderDate = Column(DateTime, default=datetime.now())
    # Relationship to parts
    # part = relationship("Part", back_populates="shop_orders")


class Part(Base):
    __tablename__ = 'parts'

    PartNumber = Column(String, nullable= False, primary_key=True)
    LayerOrder = Column(String, nullable=False)
    LayerNames = Column(String, nullable=False)

    # Relationship to shop orders
    # shop_orders = relationship("ShopOrder", back_populates="part")


def add_part(session, part_number, layer_order, layer_names):

    new_part = Part(PartNumber=part_number, LayerOrder=layer_order, LayerNames=layer_names)
    session.add(new_part)
    session.commit()

    print(f"Added part: {new_part}")

def add_shop_order(session, shop_order_number, part_number, layer_number, panel_number, images):
    # TODO: Look into Notion database API
    new_order = ShopOrder(
        ShopOrderNumber=shop_order_number,
        PartNumber=part_number,
        LayerNumber=layer_number,
        PanelNumber=panel_number,
        Images=images
    )
    # TODO: Readd date column
    session.add(new_order)
    session.commit()

    print(f"Added shop order: {new_order}")

# Create the database and table
def create_db():
    Base.metadata.create_all(engine)
    print("Database and table created successfully.")


# Usage
if __name__ == "__main__":
    # Create the database and tables
    create_db()

