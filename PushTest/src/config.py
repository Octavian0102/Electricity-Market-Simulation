from os.path import abspath
from pathlib import Path

ROOT_PATH = Path(abspath(__file__)).parent.parent
data_path = ROOT_PATH / 'data'

BATTERY_DATA = data_path / 'battery' / '02_24_2016_SP20-2_0C_DST_50SOC.csv'

E_CHARGE_DATA = data_path / 'e-charging' / 'lastprofil2017_mit_sperrzeiten_nds.csv'
HEATPUMP_DATA = data_path / 'heatpump' / 'HP_2022.csv'

PV_DATA = data_path / 'pv' / 'Solarenergie_Hochrechnung_2022.csv'
ORIGINAL_PV_POWER = 10471

NUM_INTERVALS = 96
FLEXIBILITY_START_DATE = "2022-06-12 00:15:00"
SIMULATION_DATE = "2022-06-10 00:00:00"

DAY_AHEAD_DATA = data_path / 'Prices' / 'Day_ahead_prices_2022_csv.csv'
INTRADAY_AUCTION_DATA = data_path / 'Prices' / 'intraday_quarterly_auction_2022_prices.csv'
INTRADAY_CONTINUOUS_DATA = data_path / 'Prices' / 'intraday_quarterly_continuous_2022_prices.csv'
SURVEY_DATA = data_path / 'Survey_v1.xlsx'
DAY_AHEAD_CO2_DATA = data_path / 'CO2_Emissions' / 'Day_ahead_CO2-Emissions_2022.csv'
INTRADAY_AUCTION_CO2_DATA = data_path / 'CO2_Emissions' / 'intraday_quarterly_auction_2022_CO2.csv'

# Configuration of different aggregators
# One electric vehicle, one PV plant
SMALL_AGGREGATORS = [
    {'PV': [0.2], 'battery': [0], 'heatpump': [0], 'e-charge': [1]},
    {'PV': [0.25], 'battery': [0], 'heatpump': [0], 'e-charge': [1]},
    {'PV': [0.3], 'battery': [0], 'heatpump': [0], 'e-charge': [1]},
    {'PV': [0.35], 'battery': [0], 'heatpump': [0], 'e-charge': [1]},
    {'PV': [0.4], 'battery': [0], 'heatpump': [0], 'e-charge': [1]},
    {'PV': [0.45], 'battery': [0], 'heatpump': [0], 'e-charge': [1]},
    {'PV': [0.5], 'battery': [0], 'heatpump': [0], 'e-charge': [1.05]},
    {'PV': [0.55], 'battery': [0], 'heatpump': [0], 'e-charge': [1.1]},
    {'PV': [0.6], 'battery': [0], 'heatpump': [0], 'e-charge': [1.15]},
    {'PV': [0.65], 'battery': [0], 'heatpump': [0], 'e-charge': [1]},
]
# around 100 kW max
MEDIUM_AGGREGATORS = [
    {'PV': [1], 'battery': [1], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.1], 'battery': [1], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.1], 'battery': [2], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.15], 'battery': [1], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.15], 'battery': [2], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.2], 'battery': [1], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.2], 'battery': [2], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.3], 'battery': [1], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.3], 'battery': [2], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [1.4], 'battery': [1], 'heatpump': [1], 'e-charge': [1]},
]
# at least 1 MW / 15 min
LARGE_AGGREGATORS = [
    {'PV': [2], 'battery': [1], 'heatpump': [2], 'e-charge': [1]},
    {'PV': [2], 'battery': [1], 'heatpump': [1], 'e-charge': [2]},
    {'PV': [2], 'battery': [2], 'heatpump': [1], 'e-charge': [2]},
    {'PV': [3], 'battery': [1], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [2], 'battery': [2], 'heatpump': [1], 'e-charge': [1]},
    {'PV': [2], 'battery': [1], 'heatpump': [2], 'e-charge': [1]},
    {'PV': [2], 'battery': [1], 'heatpump': [2], 'e-charge': [2]},
    {'PV': [2], 'battery': [2], 'heatpump': [2], 'e-charge': [2]},
    {'PV': [2], 'battery': [1], 'heatpump': [2], 'e-charge': [1]},
    {'PV': [2], 'battery': [1], 'heatpump': [1], 'e-charge': [2]},

]

FLEX_LIMIT = 0.1
LIMIT_FLEXIBILITY = False
