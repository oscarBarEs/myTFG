import pandas as pd

DATA_FRAME = None

def fetch_data(location):
    global DATA_FRAME
    DATA_FRAME = pd.read_json(location)
    return DATA_FRAME