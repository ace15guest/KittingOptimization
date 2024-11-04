import pandas as pd

import database
import ast
from itertools import product


def separate_layers(part_number, db_session):
    layer_names = ast.literal_eval(db_session.query(database.Part).filter_by(PartNumber=part_number).first().LayerNames.strip())
    layer_info = {}  # {Layer: {LayerInfo}: [X out list]}
    combo = {}  # {Layer: [all layer info keys]}
    for layer in layer_names:
        panels = db_session.query(database.ShopOrder).filter_by(PartNumber=part_number).filter_by(LayerNumber=layer).all()
        layer_info[layer] = {}
        for panel in panels:
            layer_info[layer][f"{panel.PartNumber}_{panel.ShopOrderNumber}_{panel.PanelNumber}_{layer}"] = panel.Images

        combo[layer] = list(layer_info[layer].keys())

    layer_combinations = list(product(*[combo[layer] for layer in layer_names], repeat=1))
    matching_algos(layer_combinations, layer_info, layer_names)
    return layer_info, combo, layer_combinations


def matching_algos(layer_combinations, layer_info, layer_names):
    panel_options = []
    good_percent = []
    wasted = []
    for option in layer_combinations:
        layers = []
        for info in option:
            layer = info.split("_")[-1]
            layers.append(ast.literal_eval(layer_info[layer][info].strip()))

        panel_length = len(layers[0])
        good_imgs = 0
        wasted_imgs = 0
        for i in range(panel_length):
            image_loc = [layers[j][i] for j in range(3)]
            img_good, imgwaste = good_parts_score(image_loc)
            good_imgs += img_good
            wasted_imgs += imgwaste

        percentage = (good_imgs / panel_length) * 100
        panel_options.append(option)
        good_percent.append(percentage)
        wasted.append(wasted_imgs)
    data = {
        "Panel Options": panel_options,
        "Percent Yield": good_percent,
        "Number Wasted": wasted
    }
    df = pd.DataFrame(data)
    df.to_csv('Output.csv', index=False)
    return


def good_parts_score(image_loc):
    #Check if Xs
    if all(item == 'O' for item in image_loc) or all(item == 'O' for item in image_loc):
        return 1, 0
    else:
        return 0, image_loc.count('O')
