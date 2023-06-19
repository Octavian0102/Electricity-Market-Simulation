from os.path import abspath
from pathlib import Path
import datetime as dt

# This config file contains scenario-independent variables and path specifications

# --- GLOBAL VARIABLES ---

T_DELTA = dt.timedelta(minutes=15) # simulation timestep size

# --- PATHS ---

# root path
ROOT_PATH = Path(abspath(__file__)).parent

# folder paths
SCENARIO_PATH = ROOT_PATH / "scenarios"
OUTPUT_PATH = ROOT_PATH / "output"
DATA_PATH = ROOT_PATH / "data"
WHEATHER_PATH = DATA_PATH / "wheather"

# wheather paths
TEMPERATURE_PATH = WHEATHER_PATH / "temperature.csv"
RADIATION_PATH = WHEATHER_PATH / "radiation.csv"

# market data paths
DAY_AHEAD_PATH = DATA_PATH / "day_ahead_prices_2022.csv"
INTRADAY_AUCTION_PATH = DATA_PATH / "intraday_quarterly_auction_2022_prices.csv"
INTRADAY_CONTINUOUS_PATH = DATA_PATH / "intraday_quarterly_continuous_2022_prices.csv"

# household data paths
PV_PATH = DATA_PATH / "pv_generation.csv"
LOAD_RESIDENTIAL_PATH = DATA_PATH / "Load_Data.csv"
