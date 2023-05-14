import datetime
from copy import deepcopy

import pandas as pd
from mango.core.agent import Agent

from PushTest.src.config import ORIGINAL_PV_POWER, NUM_INTERVALS, PV_DATA, HEATPUMP_DATA, E_CHARGE_DATA, BATTERY_DATA, \
    FLEXIBILITY_START_DATE, DAY_AHEAD_DATA, INTRADAY_CONTINUOUS_DATA, INTRADAY_AUCTION_DATA, \
    DAY_AHEAD_CO2_DATA, INTRADAY_AUCTION_CO2_DATA
from PushTest.src.survey_aggregation import Industrie_List


class AggregatorAgent(Agent):

    def __init__(self, container, unit_config):
        super().__init__(container)
        self._unit_config = unit_config
        self._aggregated_generation = []
        self._aggregated_load = []
        self._price_dict_generation = {}
        self._price_dict_load = {}
        self._utility_value = []

    async def instantiate_units(self):
        self._aggregated_generation = [0 for _ in range(NUM_INTERVALS)]
        self._aggregated_load = [0 for _ in range(NUM_INTERVALS)]
        date_list = pd.read_csv(BATTERY_DATA)['date'].tolist()
        idx = date_list.index(FLEXIBILITY_START_DATE)

        for unit_type, instances in self._unit_config.items():
            if unit_type == 'PV':
                pv_data = self.read_pv_data()
                pv_data = [entry / ORIGINAL_PV_POWER for entry in pv_data]
                pv_data = pv_data[idx:idx + NUM_INTERVALS]
                for power in instances:
                    adapted_pv_data = [entry * power for entry in deepcopy(pv_data)]
                    self._aggregated_generation = adapted_pv_data + self._aggregated_generation

            elif unit_type == 'battery':
                battery_data_charge, battery_data_discharge = self.read_battery_data()
                battery_data_charge = battery_data_charge[idx:idx + NUM_INTERVALS]
                battery_data_discharge = battery_data_discharge[idx:idx + NUM_INTERVALS]

                for scaling in instances:
                    battery_data_discharge_scaled = [-(entry * scaling) for entry in battery_data_discharge]
                    self._aggregated_generation = battery_data_discharge_scaled + self._aggregated_generation
                    battery_data_charge_scaled = [entry * scaling for entry in battery_data_charge]
                    self._aggregated_load = battery_data_charge_scaled + self._aggregated_load

            elif unit_type == 'e-charge':
                e_charge_data = self.read_e_charge_data()
                e_charge_data = e_charge_data[idx:idx + NUM_INTERVALS]
                e_charge_data = [-entry for entry in e_charge_data]
                for scaling in instances:
                    e_charge_data = [entry * scaling for entry in e_charge_data]
                    self._aggregated_load = e_charge_data + self._aggregated_load

            elif unit_type == 'heatpump':
                heatpump_data = self.read_heatpump_data()
                heatpump_data = heatpump_data[idx:idx + NUM_INTERVALS]
                heatpump_data = [-entry for entry in heatpump_data]
                for scaling in instances:
                    heatpump_data = [entry * scaling for entry in heatpump_data]
                    self._aggregated_load = heatpump_data + self._aggregated_load

    @staticmethod
    def read_battery_data():
        data = pd.read_csv(BATTERY_DATA)
        data_charge = data['Charge_Energy(Wh)'].tolist()
        del data_charge[0]
        data_charge = [float(entry.replace(',', '.')) for entry in data_charge]
        data_charge = [entry / 1000 if entry != 0 else entry for entry in data_charge]
        data_charge = [entry / 0.25 if entry != 0 else entry for entry in data_charge]

        data_discharge = data['Discharge_Energy(Wh)'].tolist()
        del data_discharge[0]
        data_discharge = [float(entry.replace(',', '.')) for entry in data_discharge]
        data_discharge = [entry / 1000 if entry != 0 else entry for entry in data_discharge]
        data_discharge = [entry / 0.25 if entry != 0 else entry for entry in data_discharge]

        return data_charge, data_discharge

    @staticmethod
    def read_e_charge_data():
        data = pd.read_csv(E_CHARGE_DATA)['Profilwert'].tolist()
        return data

    @staticmethod
    def read_heatpump_data():
        data = pd.read_csv(HEATPUMP_DATA)['kW'].tolist()
        data = [float(entry.replace(',', '.')) for entry in data]
        return data

    @staticmethod
    def read_pv_data():
        data = pd.read_csv(PV_DATA)['MW']
        data = [entry * 1000 for entry in data]
        return data

    async def limit_flexibility(self, limitation):
        kept_value = 1 - limitation
        aggregated_data = [self._aggregated_load[i] + self._aggregated_generation[i] for i in
                           range(len(self._aggregated_load))]
        return [entry * kept_value for entry in aggregated_data]

    @property
    def aggregated_generation(self):
        return self._aggregated_generation

    @property
    def aggregated_load(self):
        return self._aggregated_load

    def gate_keeper_generation(self, start_date: str, simulation_date: str, minimum_volume: int) -> dict:
        """
        The function builds a dictionary containing the dates as keyvalues from `start_date` to
        `simulation_date` and the corresponding available markets using the `aggregated_generation` and the
        lead_time as a list with binary variables in the format: [x, y, z] with x = 1 if flexibility can be used
        in the day ahead market; y = 1 if flexibility can be used in the intraday auction market; z = 1 if the
        flexibility can be used in the intraday continuous market.
        :param minimum_volume: define minimum volume in kWh as `int`
        :param start_date: Start date as string in datetime format '%Y-%m-%d %H:%M:%S'
        :param simulation_date: simulation date as string in datetime format '%Y-%m-%d %H:%M:%S'
        :return: Dictionary containing dates and corresponding lists for available markets
        """
        lead_time = datetime.datetime.strptime(simulation_date, '%Y-%m-%d %H:%M:%S') - \
                    datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        time_count = int(((datetime.datetime.strptime(simulation_date, '%Y-%m-%d %H:%M:%S') -
                           datetime.datetime.strptime(start_date,
                                                      '%Y-%m-%d %H:%M:%S')).total_seconds() / 60) / 15) + 1
        price_dict_generation = {}
        var_name = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

        for generation in self.aggregated_generation[:time_count]:
            generation_bool = generation >= minimum_volume
            if generation_bool and datetime.timedelta(minutes=540) > lead_time >= datetime.timedelta(minutes=5):
                # only intraday continuous available
                price_dict_generation[str(var_name)] = [0, 0, 1]
            elif generation_bool and datetime.timedelta(minutes=720) > lead_time >= datetime.timedelta(minutes=540):
                # intraday continuous and auction available
                price_dict_generation[str(var_name)] = [0, 1, 1]
            elif generation_bool and lead_time >= datetime.timedelta(minutes=720):
                # all markets available
                price_dict_generation[str(var_name)] = [1, 1, 1]
            else:
                # no market available
                price_dict_generation[str(var_name)] = [0, 0, 0]
            var_name += datetime.timedelta(minutes=15)

        self._price_dict_generation = price_dict_generation
        return price_dict_generation

    def gate_keeper_load(self, start_date: str, simulation_date: str, minimum_volume: int) -> dict:
        """
        The function builds a dictionary containing the dates as `datetime` keyvalues from `FLEXIBILITY_START_DATE` to
        `SIUMULATION_DATE` and the corresponding available markets using the `aggregated_load` and the
        lead_time as a list with binary variables in the format: [x, y, z] with x = 1 if flexibility can be used
        in the day ahead market; y = 1 if flexibility can be used in the intraday auction market; z = 1 if the
        flexibility can be used in the intraday continuous market.
        :param start_date: Start date as string in datetime format
        :param simulation_date: simulation date as string in datetime format
        :param minimum_volume: define minimum volume in kWh as `int`
        :return: Dictionary containing dates and corresponding lists for available markets
        """
        lead_time = datetime.datetime.strptime(simulation_date, '%Y-%m-%d %H:%M:%S') - \
                    datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        time_count = int(((datetime.datetime.strptime(simulation_date, '%Y-%m-%d %H:%M:%S') -
                           datetime.datetime.strptime(start_date,
                                                      '%Y-%m-%d %H:%M:%S')).total_seconds() / 60) / 15) + 1
        price_dict_load = {}
        var_name = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

        for load in self.aggregated_load[:time_count]:
            load_bool = load >= minimum_volume
            if load_bool and datetime.timedelta(minutes=540) > lead_time >= datetime.timedelta(minutes=5):
                # only intraday continuous available
                price_dict_load[str(var_name)] = [0, 0, 1]
            elif load_bool and datetime.timedelta(minutes=720) > lead_time >= datetime.timedelta(minutes=540):
                # intraday continuous and auction available
                price_dict_load[str(var_name)] = [0, 1, 1]
            elif load_bool and lead_time >= datetime.timedelta(minutes=720):
                # all markets available
                price_dict_load[str(var_name)] = [1, 1, 1]
            else:
                # no market available
                price_dict_load[str(var_name)] = [0, 0, 0]
            var_name += datetime.timedelta(minutes=15)
        self._price_dict_load = price_dict_load
        return price_dict_load

    def adjust_price(self, multiplier: int, desired_market: str):
        """
        Function to multiply every row of a pandas Dataframe with the specified multiplier. Therefore, it uses the
        given Price Data stored under Data (2022)
        :param multiplier: multiplies each value of the Dataframe row 'Price' with the `int` multiplier
        :param desired_market: specify which price data you want to multiply. Use either of the inputs `day_ahead` or
        `intraday_continuous` or `intraday_auction` - care for upper cases
        :return: `Pandas DataFrame` with columns 'Price' and 'Time'. Can be used analog to original Data
        """
        if desired_market == "day_ahead":
            day_ahead_csv = pd.read_csv(DAY_AHEAD_DATA, sep=";")
            day_ahead_mult = pd.DataFrame({'Price': day_ahead_csv['Price'] * multiplier, 'Time': day_ahead_csv['Time']})
            return day_ahead_mult
        elif desired_market == "intraday_continuous":
            intraday_continuous_csv = pd.read_csv(INTRADAY_CONTINUOUS_DATA, sep=";")
            intraday_continuous_mult = pd.DataFrame({'Price': intraday_continuous_csv['Price'] * multiplier,
                                                     'Time': intraday_continuous_csv['Time']})
            return intraday_continuous_mult
        elif desired_market == "intraday_auction":
            intraday_auction_csv = pd.read_csv(INTRADAY_AUCTION_DATA, sep=";")
            intraday_auction_mult = pd.DataFrame({'Price': intraday_auction_csv['Price'] * multiplier,
                                                  'Time': intraday_auction_csv['Time']})
            return intraday_auction_mult
        else:
            print("Please specify desired_market (either: day_ahead, intraday_continuous or intraday_auction) - also"
                  " care for case sensitivity")
            pass

    def utility_function_generation(self, start_date: str, simulation_date: str, minimum_volume: int) -> tuple:
        """
        The function uses `gatekeeper_generation` to check what market is utility maximizing to offer the flexibility
        from `aggregated_generation`. ATM start_date and simulation_date must be in the range of aggregated_load.
        Not more than 384 quarter-hour intervals apart.
        :param start_date: `string` value in form of '%Y-%m-%d %H:%M:%S' resembling the
        datetime the flexibility potential is recognized
        :param simulation_date: `string` value in form of '%Y-%m-%d %H:%M:%S' resembling the availability of the
        flexibility
        :param minimum_volume: define minimum volume in kWh as `int`
        :return: `tuple` with the utility, date, and market form for the utility maximizing offer
        """
        # Since day-ahead data is only available on hourly basis, the start and simulation date are rounded to the next
        # hour
        start_da = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').replace(minute=0, second=0)
        end_da = datetime.datetime.strptime(simulation_date, '%Y-%m-%d %H:%M:%S').replace(minute=0, second=0)
        # read in data and slice PD to match the time interval from start to end
        day_ahead_csv = pd.read_csv(DAY_AHEAD_DATA, sep=";")
        day_ahead_CO2_csv = pd.read_csv(DAY_AHEAD_CO2_DATA, sep=";")
        day_ahead_csv['CO2_emissions'] = day_ahead_CO2_csv['g/kWh']
        start_idx_da = day_ahead_csv.loc[day_ahead_csv['Time'] == str(start_da)].index[0]
        end_idx_da = day_ahead_csv.loc[day_ahead_csv['Time'] == str(end_da)].index[-1]
        selected_rows_da = day_ahead_csv.loc[start_idx_da:end_idx_da]
        utility_dict_da = {}
        # loop over the PD and calculate the utility for every possible case and store it in utility_dict_da
        for dates in selected_rows_da['Time']:
            if self.gate_keeper_generation(str(start_da), str(end_da), minimum_volume)[dates][0] == 1:
                # currently min lead-time to address market (720 min)
                utility_dict_da[dates] = Industrie_List[0] + Industrie_List[1] * (float(
                    day_ahead_csv.loc[day_ahead_csv['Time'] == dates]['Price']) / 1000) + Industrie_List[6] * 720 \
                                         + Industrie_List[2] * (
                                             float(day_ahead_csv.loc[day_ahead_csv['Time'] == dates]['CO2_emissions']))
        else:
            # if there are entries in the dict then store the max value and date in tuple day_ahead_max
            if utility_dict_da != {}:
                max_utility_da = max(utility_dict_da.values())
                max_date_da = [key for key, value in utility_dict_da.items() if value == max_utility_da][0]
                day_ahead_max = max_utility_da, max_date_da, "Day Ahead"
            else:
                day_ahead_max = 0, 0, "n/a"

        intraday_continuous_csv = pd.read_csv(INTRADAY_CONTINUOUS_DATA, sep=";")
        start_idx_cont = intraday_continuous_csv.loc[intraday_continuous_csv['Time'] == start_date].index[0]
        end_idx_cont = intraday_continuous_csv.loc[intraday_continuous_csv['Time'] == simulation_date].index[-1]
        selected_rows_cont = intraday_continuous_csv.loc[start_idx_cont:end_idx_cont]
        utility_dict_cont = {}
        for dates in selected_rows_cont['Time']:
            if self.gate_keeper_generation(start_date, simulation_date, minimum_volume)[dates][2] == 1:
                utility_dict_cont[dates] = Industrie_List[0] + Industrie_List[1] * (float(
                    intraday_continuous_csv.loc[intraday_continuous_csv['Time'] == dates]['Price']) / 1000) + \
                                           Industrie_List[6] * 5
        else:
            if utility_dict_cont != {}:
                max_utility_cont = max(utility_dict_cont.values())
                max_date_cont = [key for key, value in utility_dict_cont.items() if value == max_utility_cont][0]
                continuous_max = max_utility_cont, max_date_cont, "Intraday continuous"
            else:
                continuous_max = 0, 0, "n/a"

        intraday_auction_csv = pd.read_csv(INTRADAY_AUCTION_DATA, sep=";")
        intraday_auction_CO2_csv = pd.read_csv(INTRADAY_AUCTION_CO2_DATA, sep=";")
        intraday_auction_csv['CO2_emissions'] = intraday_auction_CO2_csv['gCO2/kwh']
        start_idx_auct = intraday_auction_csv.loc[intraday_auction_csv['Time'] == start_date].index[0]
        end_idx_auct = intraday_auction_csv.loc[intraday_auction_csv['Time'] == simulation_date].index[-1]
        selected_rows_auct = intraday_auction_csv[start_idx_auct:end_idx_auct]
        utility_dict_auct = {}
        for dates in selected_rows_auct['Time']:
            if self.gate_keeper_generation(start_date, simulation_date, minimum_volume)[dates][1] == 1:
                utility_dict_auct[dates] = Industrie_List[0] + Industrie_List[1] * (float(
                    intraday_auction_csv.loc[intraday_auction_csv['Time'] == dates]['Price']) / 1000) + Industrie_List[
                                               6] * 540
                + Industrie_List[2] * (
                    float(intraday_auction_csv.loc[intraday_auction_csv['Time'] == dates]['CO2_emissions']))
        else:
            if utility_dict_auct != {}:
                max_utility_auct = max(utility_dict_auct.values())
                max_date_auction = [key for key, value in utility_dict_auct.items() if value == max_utility_auct][0]
                auction_max = max_utility_auct, max_date_auction, "Intraday auction"
            else:
                auction_max = 0, 0, "n/a"

        # check what value to return. Therefore, maximize the utility and return the whole tuple.
        # if all tuples are empty then return string that the flexibility cant be used.
        if continuous_max[0] >= auction_max[0] and continuous_max[0] >= day_ahead_max[0] and continuous_max[0] != 0:
            self._utility_value = list(continuous_max)
            return continuous_max
        elif auction_max[0] >= continuous_max[0] and auction_max[0] >= day_ahead_max[0] and auction_max[0] != 0:
            self._utility_value = list(auction_max)
            return auction_max
        elif day_ahead_max[0] >= auction_max[0] and day_ahead_max[0] >= continuous_max[0] and day_ahead_max[0] != 0:
            self._utility_value = list(day_ahead_max)
            return day_ahead_max
        else:
            self._utility_value = [0, 0, "can't use flexibility"]
            return 0, 0, "can't use flexibility"
        pass

    def store_data(self):
        dates = []
        price_first = []
        price_second = []
        price_third = []
        for key, value in self._price_dict_generation.items():
            dates.append(key)
            price_first.append(value[0])
            price_second.append(value[1])
            price_third.append(value[2])
        util_value = self._utility_value + [None] * (len(dates) - len(self._utility_value))
        data = {'date': dates, 'price_0': price_first, 'price_1': price_second, 'price_2': price_third,
                'aggregated_load': self._aggregated_load[:len(dates)],
                'aggregated_generation': self._aggregated_generation[:len(dates)],
                'utility': util_value}
        df = pd.DataFrame.from_dict(data)
        df.to_csv(f'{self.aid}_{FLEXIBILITY_START_DATE}', index=False)
