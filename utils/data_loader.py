import pandas as pd

def load_csv(file):
    try:
        df = pd.read_csv(file)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        return df
    except Exception:
        return None
