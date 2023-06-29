import config

import json
import datetime as dt

class Scenario():

    def __init__(self, file):
        """
        Reads in the scenario config from the specified file and sets the config variables accordingly
        :param file: the file name for the JSON config file
        """

        self.name = file # name of the scenario [string]

        # read in the JSON file
        full_path = config.SCENARIO_PATH / (self.name + ".json")
        sc = json.load(open(full_path))

        # update the config variables
        self.t_start_str = sc["t-start"] # simulation start time [string]
        self.t_end_str = sc["t-end"] # simulation end time [string]

        self.day_ahead_closure_str = sc["day-ahead-closure"] # day-ahead market gate closure time [string]
        self.intraday_auction_closure_str = sc["intraday-auction-closure"] # intraday auction gate closure time [string]
        self.min_offer_quantity = sc["min-offer-quantity"] # minimum market offer quantity [kWh]

        self.price_average_coefficient = sc["price-average-coefficient"] # coefficient for price average calculation, non-negative [1]
        self.vola_da = sc["vola_da"] # day-ahead market volatility [1]
        self.vola_ia = sc["vola_ia"] # intraday auction market volatility [1]
        self.vola_ic = sc["vola_ic"] # intraday continuous market volatility [1]

        self.grid_price_residential = sc["grid-price-residential"] # residential grid price [€/kWh]
        self.grid_price_feedin = sc["grid-price-feedin"] # feedin grid price [€/kWh]

        self.battery_charge_min = sc["battery-charge-min"] # minimum battery charge state [kW]
        self.battery_charge_max = sc["battery-charge-max"] # maximum battery charge state [kW]
        self.battery_charge_init = sc["battery-charge-init"] # initial battery charge state [kW]

        self.pv_power_stc = sc["pv-power-stc"] # quoted pv power under STC (standard test conditions) [kW]
        self.load_multiplier = sc["load-multiplier"] # multiplier for the load data (1 = one household)

        # compute derived scenario variables
        self.t_start = dt.datetime.strptime(self.t_start_str, "%Y-%m-%d %H:%M")
        self.t_end = dt.datetime.strptime(self.t_end_str, "%Y-%m-%d %H:%M")

        self.number_of_intervals = int(((self.t_end - self.t_start).total_seconds() / 60) / 15) + 1

        self.day_ahead_closure = dt.datetime.strptime(self.day_ahead_closure_str, "%H:%M").time()
        self.intraday_auction_closure = dt.datetime.strptime(self.intraday_auction_closure_str, "%H:%M").time()
