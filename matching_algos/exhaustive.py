import pandas as pd

df = pd.read_excel(r'C:\Users\Asa Guest\PycharmProjects\KittingOptimization\Assets\ExampleDatabase.xlsx')


def exhaustive(pn=None, database: pd.DataFrame = None):
    """
    This will try all combinations of layer matching and will only terminate if there is a perfect match
    pn: A dictionary with the part number as the key and # of layers as the value {pn: # of layers}
    database: A dataframe containing all the information about the cores
    :return:
    """

    if pn is None:
        pn = {"ABC123": 4}

    pn_info = database[database['Part Number'] == list(pn.keys())[0]] # database with the desired pn filtered
    layer_nums = set(pn_info["Layer Number"]) # The layers found with the pn
    # Verifying that necessary layers are available
    if len(layer_nums) != pn[list(pn.keys())[0]]:
        raise 'Add error here'
    layer_ids = {}
    for layer in layer_nums:
        tmp_df = pn_info[pn_info['Layer Number'] == layer]
        layer_ids[layer] = {}
        for idx, row in tmp_df.iterrows():
            layer_ids[layer][row['Layer ID']] = {}
            layer_ids[layer][row['Layer ID']]['Failure'] = list(row['Failure'])
            layer_ids[layer][row['Layer ID']]['Date'] = row['Date Ran']
    return

exhaustive(database=df)
