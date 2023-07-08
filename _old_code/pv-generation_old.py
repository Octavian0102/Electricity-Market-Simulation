import config

import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

def computePVData():
    """
    Computes quarter-hourly pv data based on hourly wheather data
    """

    # read and preprocess radiation data
    df_r_raw = pd.read_csv(config.RADIATION_PATH, sep = ";")
    df_r = pd.DataFrame(df_r_raw, columns=["MESS_DATUM", "FG_LBERG"])
    for i in range(len(df_r)):
        df_r.at[i, "Time"] = dt.datetime.strptime(df_r["MESS_DATUM"][i], "%Y%m%d%H:%M").replace(minute = 0)
    df_r.drop(columns = ["MESS_DATUM"], inplace = True)
    df_r.rename(columns={"FG_LBERG": "radiation"}, inplace=True)
    df_r["radiation"] = df_r["radiation"] * 2.777778 # conversion from J/cm^2 to W/m^2

    # read and preprocess temperature data
    df_t_raw = pd.read_csv(config.TEMPERATURE_PATH, sep = ";")
    df_t = pd.DataFrame(df_t_raw, columns=["MESS_DATUM", "TT_TU"])
    for i in range(len(df_t)):
        df_t.at[i, "Time"] = dt.datetime.strptime(str(df_t["MESS_DATUM"][i]), "%Y%m%d%H")
    df_t.drop(columns = ["MESS_DATUM"], inplace = True)
    df_t.rename(columns={"TT_TU": "temperature"}, inplace=True)

    # shortening for testing purposes
    TEST_LENGTH = 100
    df_t = df_t.head(TEST_LENGTH)
    df_r = df_r.head(TEST_LENGTH)

    if(len(df_t) != len(df_r)):
        print(f"ERROR: radiation ({len(df_r)}) and temperature ({len(df_t)}) data do not match in length")
        return
    hours = len(df_t)
    
    # constants for pv computation
    NOCT = 47       # C     NOCT (nominal operating cell temperature)
    LAMB  = 0.00048 # C^-1  Temperature coefficient (war 0.004 in BA)
    T2    = 25      # C     Temperature at STC
    G     = 1000    # W/m^2 Radiation at STC

    # compute hourly pv data
    nodes = np.zeros(shape = hours+1, dtype = float) # interpolation nodes, first boundary condition is implicit here

    for i in range(hours):
        temp = df_t["temperature"][i]               # C     Air temperature
        rad = df_r["radiation"][i]                  # W/m^2 Radiation

        t1 = float(temp + (NOCT - 20)*(rad/800))  # C       Temperature of solar panel

        # in the simulation, this value is multiplied with the STC power to obtain the pv generation in kWh
        nodes[i] = float(rad * (1 - LAMB * (t1 - T2)) / G)
    
    # fill the quarter-hourly gaps through interpolation
    
    gradients = np.zeros(shape = hours+1, dtype = float) # gradients (interpolation parameters), the other two boundary conditions are implicit here
    results = np.zeros(shape = 4*hours, dtype = float) # quarter-hourly values (result)

    print(f"max index: {hours - 1}")
    # Thomas algorithm to solve for the gradients
    # initialize the upper diagonal of the matrix and right side of the equation system
    upper_diagonal = np.full(shape = hours, fill_value = -3, dtype = float)

    right_side = np.zeros(shape = hours+1, dtype = float)
    right_side[0] = 52 * nodes[0] - 10 * nodes[1]
    right_side[-1] = 52 * nodes[-1] - 42 * nodes[-2]
    for i in range(1, hours):
        right_side[i] = 52 * nodes[i] - 42 * nodes[i-1] - 10 * nodes[i+1]

    # phase 1: forward update
    upper_diagonal[0] = upper_diagonal[0] / (-8)
    for i in range(1, hours):
        upper_diagonal[i] = upper_diagonal[i] / (-8 - 11 * upper_diagonal[i-1])
    
    right_side[0] = right_side[0] / (-8)
    for i in range(1, hours+1):
        right_side[i] = (right_side[i] - 11 * right_side[i-1]) / (-8 - 11 * upper_diagonal[i-1])
    
    # phase 2: backward substitution
    gradients[-1] = right_side[-1]
    for i in range(hours-1, -1, -1):
        gradients[i] = right_side[i] - upper_diagonal[i] * gradients[i+1]

    print(gradients)

    for i in range(len(results)):
        h_index = i // 4
        value_left = nodes[h_index]
        value_right = nodes[h_index + 1]
        gradient_left = gradients[h_index]
        gradient_right = gradients[h_index + 1]

        q = (i % 4) / 4
        alpha_1 = 1 - 3* (q**2) + 2 * (q**3)
        alpha_2 = 3 * (q**2) - 2 * (q**3)
        alpha_3 = q - 2 * (q**2) + q**3
        alpha_4 = - (q**2) + q**3

        results[i] = alpha_1 * value_left + alpha_2 * value_right + alpha_3 * gradient_left + alpha_4 * gradient_right

    # construct the final data frame with quarter-hourly intervals
    df_pv = pd.DataFrame(columns = ["Time", "pv"])
    for i in range(hours):

        cur_hour = dt.datetime.strptime(str(df_t["Time"][i]), "%Y-%m-%d %H:%M:%S")
        df_pv.at[i * 4, "Time"] = cur_hour
        df_pv.at[i * 4 + 1, "Time"] = cur_hour.replace(minute = 15)
        df_pv.at[i * 4 + 2, "Time"] = cur_hour.replace(minute = 30)
        df_pv.at[i * 4 + 3, "Time"] = cur_hour.replace(minute = 45)

        df_pv.at[i * 4, "pv"] = results[i * 4]
        df_pv.at[i * 4 + 1, "pv"] = results[i * 4 + 1]
        df_pv.at[i * 4 + 2, "pv"] = results[i * 4 + 2]
        df_pv.at[i * 4 + 3, "pv"] = results[i * 4 + 3]

    df_pv.to_csv(config.PV_PATH, index = True, sep = ";")

    print(f"overall pv generation: {sum(nodes)}")
    print(f"pv generation from interpolation: {0.25 * sum(results)}")

    plt.figure(figsize = (20, 10))
    plt.plot(results, marker = "o", markersize = 4)
    #plt.plot([4*i for i in range(len(nodes))], nodes, marker = "o", markersize = 4)
    x_values = [4*i for i in range(len(nodes))]
    plt.plot(x_values, nodes, marker = "o", markersize = 4)
    plt.savefig(config.OUTPUT_PATH / "pv_plot.png")

if __name__ == "__main__":
    computePVData()
