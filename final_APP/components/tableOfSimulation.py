
from components.fromJsonToTable import fetch_data
from trame.widgets import vuetify2 as vuetify
# -----------------------------------------------------------------------------
# DATA FRAME 'output.json'
# -----------------------------------------------------------------------------

def table_of_simulation(json_file):
    header_options = {}  # Define your header options here

    DATA_FRAME = fetch_data(json_file) # en FromJsonToTable.py
    headers, rows = vuetify.dataframe_to_grid(DATA_FRAME, header_options)

    table = {
        "headers": ("headers", headers),
        "items": ("rows", rows),
        "v_model": ("selection", []),
        "search": ("query", ""),
        "classes": "elevation-1 ma-4",
        "multi_sort": True,
        "dense": True,
        "show_select": True,
        "single_select": True,
        "item_key": "id",
    }
    return table