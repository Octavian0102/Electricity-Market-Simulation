import environment as env
import config

import datetime as dt
from math import isclose

class Agent():
    """
    Models the agent and contains the algorithm for taking optimized actions
    """

    def __init__(self) -> None:
        self.market = env.Market()
        self.household = env.Household()

        self.time = dt.datetime.strptime(config.T_START, "%Y-%m-%d %H:%M:%S")

        """
        forecast_length = int((dt.timedelta(hours=48) -
                               (dt.datetime.strptime(config.DAY_AHEAD_CLOSURE, "%H:%M:%S") -
                                dt.datetime.strptime("00:00:00", "%H:%M:%S"))).total_seconds() / config.T_DELTA.total_seconds())
        """
        
        self.contracts = list() # a list of active contracts

        # variables to be determined by the agent in each action
        self.discharge = 0
        self.charge = 0
        self.grid_demand = 0
        self.grid_supply = 0
        self.offers = list()


    def run(self) -> None:
        """
        Runs the optimization over the given time for the given environment
        """

        gains = 0
        costs = 0
        violations = 0

        for index in range(config.T):
            # check if contracts need to be fulfilled at the current time
            i = 0
            while i < len(self.contracts):
                (_, delivery_time, quantity, price) = self.contracts[i]

                if(delivery_time <= self.time): # if the contract is to be fulfilled now
                    gains += price * quantity # obtain the money

                    self.contracts.pop(i) # delete the fulfilled contract from the list of open contracts
                    i -= 1
                i += 1
            
            # get the current household and market price data
            load = self.household.getLoad()
            pv = self.household.getPV()
            battery = self.household.getBattery()

            prices = self.market.getMarketPrices()
            # determine the action to take using a greedy approach
            self.greedy(load, pv, battery, prices)

            # place the recommended contracts on the market
            delivered = 0 # cumulated energy quantity to deliver to the market
            for c in self.offers:
                (_, _, q, _) = c
                delivered += q
                self.contracts.append(c)
                self.market.place_offer(c)
            # update battery state
            self.household.updateBattery(self.charge, self.discharge)

            # check the validity of the action through different constraints
            # non-negativity
            if(self.charge < 0):
                print(f"{index}: {self.time}: non-negativity charge: {self.charge}")
                violations += 1
            if(self.discharge < 0):
                print(f"{index}: {self.time}: non-negativity discharge: {self.discharge}")
                violations += 1
            if(self.grid_demand < 0):
                print(f"{index}: {self.time}: non-negativity grid_demand: {self.grid_demand}")
                violations += 1
            if(self.grid_supply < 0):
                print(f"{index}: {self.time}: non-negativity grid_supply: {self.grid_supply}")
                violations += 1

            # battery state
            battery = self.household.getBattery()
            if(battery < config.BATTERY_CHARGE_MIN):
                print(f"{index}: {self.time}: battery minimum charge: {battery}")
                violations += 1
            if(battery > config.BATTERY_CHARGE_MAX):
                print(f"{index}: {self.time}: battery maximum charge: {battery}")
                violations += 1

            # only one of grid supply/demand and battery charge/discharge
            if(self.grid_demand > 0 and self.grid_supply > 0):
                print(f"{index}: {self.time}: grid supply and demand: {self.grid_supply}; {self.grid_demand}")
                violations += 1
            if(self.charge > 0 and self.discharge > 0):
                print(f"{index}: {self.time}: battery charge and discharge: {self.charge}; {self.discharge}")
                violations += 1
            
            # load balancing
            balance = pv + self.discharge - self.charge + self.grid_demand - self.grid_supply - delivered - load
            if(not isclose(balance, 0, abs_tol=0.000001)):
                print(f"{index}: {self.time}: load balance: {balance}")
                violations += 1

            print(f"{balance} = {pv} + {self.discharge} - {self.charge} + {self.grid_demand} - {self.grid_supply} - {delivered} - {load}\n")

            costs += self.grid_demand * config.GRID_PRICE_RESIDENTIAL
            gains += self.grid_supply * config.GRID_PRICE_FEEDIN

            self.time = self.time + config.T_DELTA

        print(f"\nCumulated gains from market offers and grid feed-in: {gains}")
        print(f"Cumulated costs from grid demand: {costs}")
        print(f"Constraint violations: {violations}")


    def greedy(self, load, pv, battery, prices : dict()) -> None:
        """
        Decides what offers to place on the different markets, given the current market and household state
        """
        # reset the variables to be determined in this action
        self.discharge = 0
        self.charge = 0
        self.grid_demand = 0
        self.grid_supply = 0
        self.offers = list()

        surplus = pv - load

        # first, satisfy own demand when the base load is higher than the pv generation
        if(surplus < 0):
            # use the battery if possible
            if(surplus + battery >= 0):
                self.discharge = - surplus # discharge the battery partially to satisfy base load
                print("Action: partial discharge")
            else:
                self.discharge = battery # discharge the battery fully
                self.grid_demand = - (battery + surplus) # fulfill the remaining demand from the grid
                print("Action: full discharge with grid demand")
            return # in this case, no offers are placed

        if(surplus + battery < config.MIN_OFFER_QUANTITY):
            if(battery + surplus < config.BATTERY_CHARGE_MAX):
                self.charge = surplus # charge the battery with the energy surplus and place no market offers
                print("Action: charge due to insufficient quantity")
            else:
                self.charge = config.BATTERY_CHARGE_MAX - battery # fully charge the battery
                self.grid_supply = surplus - self.charge # feed the remaining energy into the grid
                print("Action: partial charge and grid supply due to insufficient quantity")
            return

        # determine the best market to currently place an offer, i.e. the market with the highest current price
        best_market = max(prices, key=prices.get)
        best_price = prices[best_market]

        # check whether the market price is higher than the grid residential price
        if(best_price > config.GRID_PRICE_RESIDENTIAL):
            self.discharge = battery # if yes, fully discharge the battery to offer this energy on the market
            self.offers.append((best_market, self.time, surplus + battery, best_price)) # construct the market offer
            print(f"Action: market offer at {best_market} for {best_price} €/kWh")
        else:
            # if no, use the energy to charge the battery or feed it into the grid
            if(battery + surplus < config.BATTERY_CHARGE_MAX):
                self.charge = surplus # charge the battery with the energy surplus and place no market offers
                print(f"Action: charge due to small price at {best_market} of {best_price} €/kWh")
            else:
                self.charge = config.BATTERY_CHARGE_MAX - battery # fully charge the battery
                self.grid_supply = surplus - self.charge # feed the remaining energy into the grid
                print(f"Action: partial charge and grid supply due to small price at {best_market} of {best_price} €/kWh")
            return
