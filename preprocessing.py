import pandas as pd
import config

load_data = pd.read_csv(config.LOAD_RESIDENTIAL_PATH, sep=";")
electricity_demand = load_data.dropna()




