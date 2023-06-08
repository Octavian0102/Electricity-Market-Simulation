
import pandas as pd
import config
import datetime as dt

class Market():
    """
    Contains the market model, including market prices at different times, and handles offers placed by the agent
    """

    def __init__(self):
        self.time_index = 0
        self.current_time = dt.datetime.strptime(config.T_START, "%Y-%m-%d %H:%M:%S")

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
        # TODO do we need the for statement in here? Should also work with just /1000
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
        #TODO Discuss whether this simplification can be justified to some extend
        result = dict()
        result["DA"] = self.prices_DA["Price"][self.time_index // 4]
        result["IA"] = self.prices_IA["Price"][self.time_index]
        result["IC"] = self.prices_IC["Price"][self.time_index]
        
        self.time_index += 1
        self.current_time = self.current_time + config.T_DELTA
        return result


    def getMarketprediction(self) -> dict:
        result = dict()
        if self.time_index >= 4:
            result["DA"] = float(self.prices_DA["Price"][(self.time_index // 4)-1]) * config.LAMBDA + \
                           float(self.prices_DA["Price"][self.time_index//4]) * (1-config.LAMBDA)
            result["IA"] = float(self.prices_IA["Price"][(self.time_index - 1)]) * config.LAMBDA + \
                           float(self.prices_IA["Price"][self.time_index]) * (1-config.LAMBDA)
            result["IC"] = float(self.prices_IC["Price"][(self.time_index - 1)]) * config.LAMBDA + \
                           float(self.prices_IC["Price"][self.time_index]) * (1 - config.LAMBDA)

        else:
            result["DA"] = self.prices_DA["Price"][self.time_index // 4]
            result["IA"] = self.prices_IA["Price"][self.time_index]
            result["IC"] = self.prices_IC["Price"][self.time_index]
        self.time_index += 1
        return result


    def place_offer(self, offer) -> bool:
        """
        Places an offer on the given market with the respective specifications.
        These include the market (DA, ...), the delivery time, the quantity and the offer price
        :param offer: the offer to be placed
        """

        res = True
        market, del_time, quantity, _ = offer
        compare_time = self.current_time - config.T_DELTA

        print(f"Placing offer at {market} for {del_time} of {quantity}, current time {compare_time}")

        if(quantity < config.MIN_OFFER_QUANTITY):
            print("Minimum offer quantitiy not satisfied")
            res = False
        
        # check gate closure time
        if(market == "DA"):
            if(del_time.date() <= compare_time.date()):
                print("DA: wrong date")
                res = False
            if(dt.datetime.strptime(config.DAY_AHEAD_CLOSURE, "%H:%M:%S").time() <= compare_time.time()):
                print("DA: wrong time")
                res = False

        if(market == "IA"):
            if(del_time.date() <= compare_time.date()):
                print("IA: wrong date")
                res = False
            if(dt.datetime.strptime(config.INTRADAY_AUCTION_CLOSURE, "%H:%M:%S").time() <= compare_time.time()):
                print("IA: wrong time")
                res = False

        if(market == "IC"):
            if(del_time.date() <= compare_time.date()):
                print("IC: wrong date")
                res = False
            if(del_time.time() <= compare_time.time()):
                print("IC: wrong time")
                res = False

        return res


class Household():
    """
    Models the state of the household of the agent, including the battery and the pv system
    """

    def __init__(self):
        self.time_index = 0
        self.load = pd.read_csv(config.LOAD_RESIDENTIAL_PATH, sep=";")
        self.load = self.load.dropna()

        # read in load data; for the beginning, the load is constant
        # self.load = [config.LOAD_CONSTANT] * config.T
        self.load = self.load.loc[self.load["Time"] >= config.T_START]
        self.load.reset_index(drop=True, inplace=True)

        self.battery_state = config.BATTERY_CHARGE_INIT

        # read in PV data
        # TODO get actual PV Data (Daniel)
        self.pv = pd.read_csv(config.PV_PATH, sep=",")
        self.pv.rename(columns={"date": "Time", "MW": "Amount"}, inplace=True)
        self.pv = self.pv.loc[self.pv["Time"] >= config.T_START]
        self.pv.reset_index(drop=True, inplace=True)

        # scale PV data appropriately
        for i in range(len(self.pv)):
            self.pv.at[i, "Amount"] = self.pv["Amount"][i] / 100 # arbitrarily chosen constant !?
        
    def getPV(self) -> float:
        """
        :return: the PV generation data known to the agent at the current time
        """

        result = self.pv["Amount"][self.time_index]
        self.time_index += 1

        return result
    
    def getLoad(self) -> float:
        """
        :return: current base load
        """
        result = self.load["Sum [kWh]"][self.time_index]
        self.time_index += 1
        return result
    
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
