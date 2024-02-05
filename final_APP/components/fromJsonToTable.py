import pandas as pd

DATA_FRAME = None

def fetch_data(location):
    global DATA_FRAME
    data = pd.read_json(location)
    DATA_FRAME = pd.DataFrame(data)
    return DATA_FRAME