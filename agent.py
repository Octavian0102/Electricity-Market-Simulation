import environment as env
import config

import datetime as dt

class Agent():
    """
    Models the agent and contains the algorithm for taking optimized actions
    """

    def __init__(self) -> None:
        self.market = env.Market()
        self.household = env.Household()

        forecast_length = int((dt.timedelta(hours=48) -
                               (dt.datetime.strptime(config.DAY_AHEAD_CLOSURE, "%H:%M:%S") -
                                dt.datetime.strptime("00:00:00", "%H:%M:%S"))).total_seconds() / config.T_DELTA.total_seconds())
        
        self.battery_forecast = [0] * forecast_length # initialize battery forecast

        self.contracts = list()


    def run(self) -> None:
        """
        Runs the optimization over the given time for the given environment
        """

        time = dt.datetime.strptime(config.T_START, "%Y-%m-%d %H:%M:%S")
        gains = 0

        for index in range(config.T):
            # TODO check if contracts need to be fulfilled at the current time
            
            load = self.household.getLoad()
            pv = self.household.getPV()

            prices = self.market.getMarketPrices()

            actions = self.greedy(load, pv, prices, index, time)

            for c in actions:
                self.contracts.append(c)
                self.market.take_action(c)

            time = time + config.T_DELTA


    def greedy(self, load, pv, prices : dict(), index : int, time : dt.datetime) -> list():
        """
        Decides what offers to place on the different markets, given the current market and household state
        :return: a list containing the actions to take in the current state
        """
        # TODO implement heuristic to decide what offers to place
        
        # for each market where it is possilbe to place an offer
        # satisfy own demand first, using the battery if necessary

        # check whether the market price would be higher than the grid residential price
        # if yes, offer on the market

        # if no, save the energy to the battery

        # if the battery is already full, allocate the remaining energy as grid feed-in

