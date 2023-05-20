
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
        self.prices_DA = pd.read_csv(config.DAY_AHEAD_PATH, sep=";", index_col='Time') # TODO handle hourly prices
        self.prices_IA = pd.read_csv(config.INTRADAY_AUCTION_PATH, sep=";", index_col='Time')
        self.prices_IC = pd.read_csv(config.INTRADAY_CONTINUOUS_PATH, sep=";", index_col='Time')
        # slice DataFrame to the relevant sequence from start to end from config and transforms to kWh
        self.relevant_IA_prices = self.prices_IA.loc[config.T_START:]/1000
        self.relevant_IC_prices = self.prices_IC.loc[config.T_START:]/1000
        self.relevant_DA_prices = self.prices_DA.loc[config.T_START:]/1000

    def getMarketPrices(self) -> dict:
        """
        Gives the current market prices as a dictionary.
        The keys are the different markets
        and the values are the respective market prices
        """
        result = dict()
        if self.t == 0:
            result['DA'] = self.relevant_DA_prices.iloc[12:36]
            result['IA'] = self.relevant_IA_prices.iloc[48:144]
        elif self.t == 16:
            result['IA'] = self.relevant_IA_prices.iloc[144:240]
        elif self.t - 16 % 96 == 0:
            result['IA'] = self.relevant_IA_prices.iloc[self.t + 48:self.t + 144]
        elif self.t % 96 == 0:
            result['DA'] = self.relevant_DA_prices.iloc[(self.t / 4) + 12:(self.t / 4) + 36]
        result['IC'] = self.relevant_IC_prices.iloc[self.t + 1]
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
