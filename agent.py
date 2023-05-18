import environment as env
import config

class Agent():
    """
    Models the agent and contains the algorithm for taking optimized actions
    """

    def __init__(self) -> None:
        self.market = env.Market() # TODO insert correct arguments
        self.household = env.Household()

        self.contracts = []


    def run(self) -> None:
        """
        
        """

        pv_day = self.household.getPV()

        for time in range(): # TODO set upper limit based on config T_END
            # TODO check if contracts need to be fulfilled at the current time

            prices = self.market.getMarketPrices()
            action = self.greedy(pv_day, prices)

            # TODO take actions returned by the greedy algorithm, i.e. make the respective contracts
            

    def greedy(self, pv, prices) -> list():
        """
        
        """
        # TODO implement heuristic to decide what offers to place
        pass
