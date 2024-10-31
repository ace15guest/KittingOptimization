import database
import ast


def separate_layers(part_number, db_session):
    layer_names = ast.literal_eval(db_session.query(database.Part).filter_by(PartNumber=part_number).first().LayerNames.strip())
    info = {}
    for layer in layer_names:
        panels = db_session.query(database.ShopOrder).filter_by(PartNumber=part_number).filter_by(LayerNumber=layer).all()
        info[layer] = {}
        for panel in panels:
            info[layer][f"{panel.PartNumber}_{panel.ShopOrderNumber}_{panel.PanelNumber}"] = panel.Images



    return info
