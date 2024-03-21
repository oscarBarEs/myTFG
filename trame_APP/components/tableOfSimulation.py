
from trame.widgets import vuetify2 as vuetify
import pandas as pd
import altair as alt
# -----------------------------------------------------------------------------
# DATA FRAME 'output.json'
# -----------------------------------------------------------------------------
DATA_FRAME = None

def table_of_simulation(json_file):
    header_options = {"Id's Reen": {"sortable": False}}  # Define your header options here

    global DATA_FRAME 
    DATA_FRAME= pd.DataFrame(json_file) 
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
        "single_select": False,
        "item_key": "Id's Reen",
    }
    return table

def selection_change_tos(selection=[], **kwargs):
    global DATA_FRAME
    # Filter the DataFrame to only include rows where the 'Id's Reen' value is in selection
    filtered_data =  pd.DataFrame(selection)
    if filtered_data.empty:
        grouped_data = DATA_FRAME.groupby('Segmentos Reen').size().reset_index(name='counts')

        return alt.Chart(grouped_data).mark_bar().encode(
            x='Segmentos Reen:O',
            y='counts:Q'
        ).properties(width='container', height=100)

    grouped_data = filtered_data.groupby('Segmentos Reen').size().reset_index(name='counts')

    # Chart
    chart = alt.Chart(grouped_data).mark_bar().encode(
        x='Segmentos Reen:O',
        y='counts:Q'
    ).properties(width='container', height=100)
    
    return chart

def full_chart(_data):
    current_data = pd.DataFrame(_data)
    grouped_data = current_data.groupby('Segmentos Reen').size().reset_index(name='counts')
    return alt.Chart(grouped_data).mark_bar().encode(
        x='Segmentos Reen:O',
        y='counts:Q'
    ).properties(width='container', height=100)    

def chart_onset_pacing(selection=[], **kwargs):
    global DATA_FRAME
    chart = alt.Chart(DATA_FRAME).mark_point().encode(
        x='Segmento AHA:Q',
        y='Segmento Reen:Q'
    ).properties(width='container', height=100)
    
    return chart