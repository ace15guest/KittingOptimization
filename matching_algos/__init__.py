import pandas as pd

import database
import ast
from itertools import product


def separate_layers(part_number, db_session):
    # Get the layer names of the part number
    layer_names = ast.literal_eval(db_session.query(database.Part).filter_by(PartNumber=part_number).first().LayerNames.strip())
    layer_info = {}  # Structure is as follows {Layer: {LayerInfo}: [X out list]}
    combo = {}  # Structure is as follows {Layer: [all layer info keys]}
    for layer in layer_names:
        panels = db_session.query(database.ShopOrder).filter_by(PartNumber=part_number).filter_by(LayerNumber=layer).all()
        layer_info[layer] = {}
        for panel in panels:
            layer_info[layer][f"{panel.PartNumber}_{panel.ShopOrderNumber}_{panel.PanelNumber}_{layer}"] = panel.Images

        combo[layer] = list(layer_info[layer].keys())

    layer_combinations = list(product(*[combo[layer] for layer in layer_names], repeat=1))
    optimized_layer_combos = all_comb_brute(layer_combinations, layer_info, layer_names)
    return optimized_layer_combos


def all_comb_brute(layer_combinations, layer_info, layer_names):
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
            image_loc = [layers[j][i] for j in range(len(layer_names))]
            img_good, imgwaste = good_parts_score(image_loc)
            good_imgs += img_good
            wasted_imgs += imgwaste

        percentage = (good_imgs / panel_length) * 100
        panel_options.append(option)
        good_percent.append(percentage)
        wasted.append(wasted_imgs)
    data = {}
    for idx, layer in enumerate(layer_names):
        cur_layer = [layer_combinations[i][idx] for i in range(len(layer_combinations))]
        data[layer] = cur_layer

    data["Percent Yield"] = good_percent
    data["Number Wasted"] = wasted

    df = pd.DataFrame(data)
    # df.to_csv('All_Combinations.csv', index=False)
    return make_matches(df)

def make_matches(df):
    equip = []
    df = df.sort_values('Number Wasted')
    wasted_vals = set(df["Number Wasted"])
    for waste_val in wasted_vals:
        matches_exist = True
        while matches_exist:
            temp_df = df.loc[df['Number Wasted'] == waste_val]
            temp_df = temp_df.sort_values('Percent Yield', ascending=False)
            temp_df = temp_df.reset_index(drop=True)
            if len(temp_df) == 0:
                break
            match_made = temp_df.loc[0]
            equip.append(match_made)

            for col in temp_df.columns:
                if str(col) in ["Percent Yield", "Number Wasted"]:
                    continue
                else:
                    df = df[df[col] != match_made[col]]
    out_data = pd.DataFrame(equip)
    out_data.reset_index(inplace=True, drop=True)
    return out_data









def good_parts_score(image_loc):
    #Check if Xs
    if all(item == 'O' for item in image_loc) or all(item == 'O' for item in image_loc):
        return 1, 0
    else:
        return 0, image_loc.count('O')
