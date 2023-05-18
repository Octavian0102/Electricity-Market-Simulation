from os.path import abspath
from pathlib import Path
import datetime

# global variables

T_START = "2022-07-01 12:00:00"
T_END = "2022-07-03 12:00:00"
T = int(((datetime.datetime.strptime(T_END, '%Y-%m-%d %H:%M:%S') -
          datetime.datetime.strptime(T_START, '%Y-%m-%d %H:%M:%S')).total_seconds() / 60) / 15) + 1

LOAD_CONSTANT = 50 # constant base load for the household [kWh]

BATTERY_CHARGE_MIN = 0 # minimum battery charge state [kW]
BATTERY_CHARGE_MAX = 1000 # maximum battery charge state [kW]
BATTERY_CHARGE_INIT = BATTERY_CHARGE_MIN # initial battery charge state [kW]
# TODO add battery efficiency constants when needed

GRID_PRICE_RESIDENTIAL = 0.3 # grid residential price [€/kWh]
GRID_PRICE_FEEDIN = 0.07 # grid feedin price [€/kWh]

# paths

ROOT_PATH = Path(abspath(__file__)).parent.parent
data_path = ROOT_PATH / 'data'

PV_PATH = data_path / 'pv_generation.csv'
DAY_AHEAD_PATH = data_path / 'day_ahead_prices_2022.csv'
INTRADAY_AUCTION_PATH = data_path / 'intraday_quarterly_auction_2022_prices.csv'
INTRADAY_CONTINUOUS_PATH = data_path / 'intraday_quarterly_continuous_2022_prices.csv'
