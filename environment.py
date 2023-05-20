
import pandas as pd
import config

import datetime as dt

class Market():
    """
    Contains the market model, including market prices at different times, and handles offers placed by the agent
    """

    def __init__(self):
        self.time_index = 0
        self.current_time = config.T_START

        # read in price data
        self.prices_DA = pd.read_csv(config.DAY_AHEAD_PATH, sep=";")
        self.prices_IA = pd.read_csv(config.INTRADAY_AUCTION_PATH, sep=";")
        self.prices_IC = pd.read_csv(config.INTRADAY_CONTINUOUS_PATH, sep=";")

        # slice DataFrame to the relevant sequence from start to end from config
        self.prices_DA = self.prices_DA.loc[self.prices_DA["Time"] >= config.T_START]
        self.prices_DA.reset_index(drop=True, inplace=True)

        self.prices_IA = self.prices_IA.loc[self.prices_IA["Time"] >= config.T_START]
        self.prices_IA.reset_index(drop=True, inplace=True)

        self.prices_IC = self.prices_IC.loc[self.prices_IC["Time"] >= config.T_START]
        self.prices_IC.reset_index(drop=True, inplace=True)

        # transform prices to [€/kWh]
        for i in range(len(self.prices_DA)):
            self.prices_DA.at[i, "Price"] = self.prices_DA["Price"][i] / 1000
            self.prices_IA.at[i, "Price"] = self.prices_IA["Price"][i] / 1000
            self.prices_IC.at[i, "Price"] = self.prices_IC["Price"][i] / 1000


    def getMarketPrices(self) -> dict:
        """
        Gives the current market prices as a dictionary.
        The keys are the different markets
        and the values are the respective market prices
        """
        result = dict()
        result["DA"] = self.prices_DA["Price"][self.time_index // 4]
        result["IA"] = self.prices_IA["Price"][self.time_index]
        result["IC"] = self.prices_IC["Price"][self.time_index]
        """
        if self.t == 0:
            result['DA'] = self.relevant_DA_prices.iloc[12:36]
            result['IA'] = self.relevant_IA_prices.iloc[48:144]
        elif self.t == 16:
            result['IA'] = self.relevant_IA_prices.iloc[144:240]
        elif self.t - 16 % 96 == 0:
            result['IA'] = self.relevant_IA_prices.iloc[self.t + 48:self.t + 144]
        elif self.t % 96 == 0:
            result['DA'] = self.relevant_DA_prices.iloc[int(self.t / 4) + 12: int(self.t / 4) + 36]
        result['IC'] = self.relevant_IC_prices.iloc[self.t + 1]
        """
        self.time_index += 1
        return result

    def place_offer(self, offer) -> None:
        """
        Places an offer on the given market with the respective specifications.
        These include the market (DA, ...), the delivery time, the quantity and the offer price
        :param offer: the offer to be placed
        """
        print(f"Offer placed: {offer}")


class Household():
    """
    Models the state of the household of the agent, including the battery and the pv system
    """

    def __init__(self):
        self.t = 0

        # read in load data; for the beginning, the load is constant
        self.load = [config.LOAD_CONSTANT] * config.T

        self.battery_state = config.BATTERY_CHARGE_INIT

        # read in PV data
        self.pv = pd.read_csv(config.PV_PATH, sep=",")
        self.pv.rename(columns = {"date": "Time", "MW": "Amount"}, inplace = True)
        self.pv = self.pv.loc[self.pv["Time"] >= config.T_START]
        self.pv.reset_index(drop=True, inplace=True)

        # scale PV data appropriately
        for i in range(len(self.pv)):
            self.pv.at[i, "Amount"] = self.pv["Amount"][i] / 100 # arbitrarily chosen constant !?
        
    def getPV(self) -> float:
        """
        :return: the PV generation data known to the agent at the current time
        """

        result = self.pv["Amount"][self.t]
        self.t += 1

        return result
    
    def getLoad(self) -> float:
        """
        :return: current base load
        """

        return self.load[self.t]
    
    def getBattery(self) -> float:
        """
        :return: current battery state
        """

        return self.battery_state
    
    def updateBattery(self, charge, discharge) -> None:
        """
        Update the state of the battery
        :param charge: battery charge amount
        :param discharge: battery discharge amount
        """

        self.battery_state += charge - discharge
