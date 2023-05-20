import pandas as pd
import config

import datetime as dt

class Market():
    """
    Contains the market model, including market prices at different times and handles offers placed by the agent
    """

    def __init__(self):
        self.t = 0

        # read in price data
        self.prices_DA = pd.read_csv(config.DAY_AHEAD_PATH, sep=";") # TODO handle hourly prices
        self.prices_IA = pd.read_csv(config.INTRADAY_AUCTION_PATH, sep=";")
        self.prices_IC = pd.read_csv(config.INTRADAY_CONTINUOUS_PATH, sep=";")
        # TODO extract relevant prices based on config dates (datetime)
        # TODO transform MWh to kWh


    def getMarketPrices(self) -> dict:
        """
        Gives the current market prices as a dictionary.
        The keys are the different markets
        and the values are the respective market prices
        """

        result = dict()
        result["DA"] = self.prices_DA["Price"] # TODO select prices from the next day
        result["IA"] = 0 # TODO
        result["IC"] = 0 # TODO

        self.t += 1

        return result

    def take_action(self, action) -> None:
        """
        Executes the action(s) taken by the agent
        :param action: the action(s) as 
        """


class Household():
    """
    Models the state of the household of the agent, including the battery and the pv system
    """

    def __init__(self):
        self.t = 0

        # read in load data; for the beginning, the load is constant
        self.load = config.LOAD_CONSTANT

        self.battery_state = config.BATTERY_CHARGE_INIT

        # read in PV data
        self.pv = pd.read_csv(config.PV_PATH, sep=",") # TODO rename MW to kW

    def getPV(self) -> float:
        """
        :return: the PV generation data known to the agent at the current time
        """

        self.t += 1

        return self.pv # TODO select pv generation w.r.t time
    
    def getLoad(self) -> float:
        """
        :return: current base load
        """

        return self.load
