
from trame.widgets import vuetify2 as vuetify
import pandas as pd
import altair as alt
# -----------------------------------------------------------------------------
# DATA FRAME 'output.json'
# -----------------------------------------------------------------------------
DATA_FRAME = None
heightOfChart = 250
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
        "item_key": "idSim",
    }
    return table

def chart_Reen_Count(selection=[], **kwargs):
    global DATA_FRAME
    # Filter the DataFrame to only include rows where the 'Id's Reen' value is in selection
    filtered_data =  pd.DataFrame(selection)
    if filtered_data.empty:
        grouped_data = DATA_FRAME.groupby('Segmentos Reen').size().reset_index(name='counts')

        return alt.Chart(grouped_data).mark_bar().encode(
            x='Segmentos Reen:O',
            y='counts:Q'
        ).properties(width='container', height=heightOfChart)

    grouped_data = filtered_data.groupby('Segmentos Reen').size().reset_index(name='counts')

    # Chart
    chart = alt.Chart(grouped_data).mark_bar().encode(
        x='Segmentos Reen:O',
        y='counts:Q'
    ).properties(width='container', height=heightOfChart)
    
    return chart
  

def chart_onset_pacing(selection=[], **kwargs):
    filtered_data =  pd.DataFrame(selection)
    if filtered_data.empty:
        global DATA_FRAME
        grouped_data = DATA_FRAME.groupby(['Segmento AHA', 'Segmentos Reen']).size().reset_index(name='counts')

        return alt.Chart(grouped_data).mark_point().encode(
            x='Segmentos Reen:Q',
            y='Segmento AHA:Q',
            size='counts:Q',
            color=alt.Color('counts:Q', scale=alt.Scale(domain=[0,  grouped_data['counts'].max()], range=['green', 'red']))
        ).properties(width='container', height=heightOfChart)
    
    filtered_data['Segmentos Reen'] = filtered_data['Segmentos Reen'].astype(float).astype(int)  # convert to float, then to integer
    filtered_data['Segmento AHA'] = filtered_data['Segmento AHA'].astype(float).astype(int)  # convert to float, then to integer
    grouped_data = filtered_data.groupby(['Segmento AHA', 'Segmentos Reen']).size().reset_index(name='counts')

    chart = alt.Chart(grouped_data).mark_point().encode(
        x='Segmentos Reen:Q',
        y='Segmento AHA:Q',
        size='counts:Q',  # encode the size of the points with the count
        color=alt.Color('counts:Q', scale=alt.Scale(domain=[0, grouped_data['counts'].max()], range=['green', 'red']))  # encode the color with the count

    ).properties(width='container', height=heightOfChart)
    
    return chart


# {'idSim': 3, "Id's Reen": '45147', 'Segmentos Reen': '16.0', 'stimFrecS1': '600.0', 'stimFrecS2': '295.0', 'nStimsS1': '6', 'nStimsS2': '3', 'cv_memory': '0.05', 'apd_memory': '0.35', 'APDR factor': '1.0', 'CVR factor': '1.0', 'apd_isot_ef': '0.8', 'id_extraI': '96899', 'Segmento AHA': '7.0', 'Endo/Epi': 'Endo'}
