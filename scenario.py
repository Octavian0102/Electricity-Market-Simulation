import config

import json
import datetime as dt

class Scenario():

    def __init__(self, file):
        """
        Reads in the scenario config from the specified file and sets the config variables accordingly
        :param file: the file name for the JSON config file
        """

        # read in the JSON file
        full_path = config.SCENARIO_PATH / file
        sc = json.load(open(full_path))

        # update the config variables
        self.t_start_str = sc["t-start"]
        self.t_end_str = sc["t-end"]

        self.day_ahead_closure_str = sc["day-ahead-closure"]
        self.intraday_auction_closure_str = sc["intraday-auction-closure"]
        self.min_offer_quantity = sc["min-offer-quantity"]

        self.price_average_coefficient = sc["price-average-coefficient"]
        self.vola_da = sc["vola_da"]
        self.vola_ia = sc["vola_ia"]
        self.vola_ic = sc["vola_ic"]

        self.grid_price_residential = sc["grid-price-residential"]
        self.grid_price_feedin = sc["grid-price-feedin"]

        self.battery_charge_min = sc["battery-charge-min"]
        self.batter_charge_max = sc["battery-charge-max"]
        self.batter_charge_init = sc["battery-charge-init"]

        self.pv_power_stc = sc["pv-power-stc"]

        # compute derived scenario variables
        self.t_start = dt.datetime.strptime(self.t_start_str, "%Y-%m-%d %H:%M")
        self.t_end = dt.datetime.strptime(self.t_end_str, "%Y-%m-%d %H:%M")

        self.number_of_intervals = int(((self.t_end - self.t_start).total_seconds() / 60) / 15) + 1

        self.day_ahead_closure = dt.datetime.strptime(self.day_ahead_closure_str, "%H:%M").time()
        self.intraday_auction_closure = dt.datetime.strptime(self.intraday_auction_closure_str, "%H:%M").time()
