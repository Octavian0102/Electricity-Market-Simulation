from os.path import abspath
from pathlib import Path
import datetime as dt

# global variables

# simulation time
T_START_STR = "2022-07-01 12:00:00"
T_END_STR = "2022-07-04 12:00:00"

T_START = dt.datetime.strptime(T_START_STR, "%Y-%m-%d %H:%M:%S")
T_END = dt.datetime.strptime(T_END_STR, "%Y-%m-%d %H:%M:%S")

# number of quarter hours between start and end time
T = int(((T_END - T_START).total_seconds() / 60) / 15) + 1

T_DELTA = dt.timedelta(minutes=15) # simulation timestep size

# gate closure times
DAY_AHEAD_CLOSURE_STR = "12:00:00"
INTRADAY_AUCTION_CLOSURE_STR = "16:00:00"

DAY_AHEAD_CLOSURE = dt.datetime.strptime(DAY_AHEAD_CLOSURE_STR, "%H:%M:%S").time()
INTRADAY_AUCTION_CLOSURE = dt.datetime.strptime(INTRADAY_AUCTION_CLOSURE_STR, "%H:%M:%S").time()

MIN_OFFER_QUANTITY = 100 # minimum quantity to offer on a market [kWh]

LAMBDA = 0 # non-negative, LAMBDA = 0 leads to prices not being averaged over time
VOLA_DA = 0
VOLA_IA = 0
VOLA_IC = 0

# grid constants
GRID_PRICE_RESIDENTIAL = 0.3 # grid residential price [€/kWh]
GRID_PRICE_FEEDIN = 0.07 # grid feedin price [€/kWh]

LOAD_CONSTANT = 50 # constant base load for the household [kWh]

BATTERY_CHARGE_MIN = 0 # minimum battery charge state [kW]
BATTERY_CHARGE_MAX = 100 # maximum battery charge state [kW]
BATTERY_CHARGE_INIT = BATTERY_CHARGE_MIN # initial battery charge state [kW]

# paths

ROOT_PATH = Path(abspath(__file__)).parent
data_path = ROOT_PATH / "data"

PV_PATH = data_path / "pv_generation.csv"
DAY_AHEAD_PATH = data_path / "day_ahead_prices_2022.csv"
INTRADAY_AUCTION_PATH = data_path / "intraday_quarterly_auction_2022_prices.csv"
INTRADAY_CONTINUOUS_PATH = data_path / "intraday_quarterly_continuous_2022_prices.csv"
LOAD_RESIDENTIAL_PATH = data_path / "Load_Data.csv"
