import database
import ast
from itertools import product


def separate_layers(part_number, db_session):
    layer_names = ast.literal_eval(db_session.query(database.Part).filter_by(PartNumber=part_number).first().LayerNames.strip())
    layer_info = {} # {Layer: {LayerInfo}: [X out list]}
    combo = {} # {Layer: [all layer info keys]}
    for layer in layer_names:
        panels = db_session.query(database.ShopOrder).filter_by(PartNumber=part_number).filter_by(LayerNumber=layer).all()
        layer_info[layer] = {}
        for panel in panels:
            layer_info[layer][f"{panel.PartNumber}_{panel.ShopOrderNumber}_{panel.PanelNumber}_{layer}"] = panel.Images

        combo[layer] = list(layer_info[layer].keys())

    layer_combinations = list(product(*[combo[layer] for layer in layer_names], repeat=1))
    return layer_info, combo, layer_combinations
