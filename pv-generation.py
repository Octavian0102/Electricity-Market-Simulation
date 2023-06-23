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
    #TEST_LENGTH = 100
    #df_t = df_t.head(TEST_LENGTH)
    #df_r = df_r.head(TEST_LENGTH)

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
    nodes = np.zeros(shape = hours+1, dtype = float) # interpolation nodes, boundary condition is implicit here

    for i in range(hours):
        temp = df_t["temperature"][i]               # C     Air temperature
        rad = df_r["radiation"][i]                  # W/m^2 Radiation

        t1 = float(temp + (NOCT - 20)*(rad/800))  # C       Temperature of solar panel

        # in the simulation, this value is multiplied with the STC power to obtain the pv generation in kWh
        nodes[i] = float(rad * (1 - LAMB * (t1 - T2)) / G)
        if(nodes[i] < 0): nodes[i] = 0
    
    # fill the quarter-hourly gaps through interpolation
    
    gradients = np.zeros(shape = hours+1, dtype = float) # gradients (interpolation parameters)
    for i in range(1, hours+1):
        gradients[i] = nodes[i] - nodes[i-1] # linear interpolation

    # construct the final data frame with quarter-hourly intervals
    df_pv = pd.DataFrame(columns = ["Time", "pv"])
    for i in range(hours):

        cur_hour = dt.datetime.strptime(str(df_t["Time"][i]), "%Y-%m-%d %H:%M:%S")
        df_pv.at[i * 4, "Time"] = cur_hour
        df_pv.at[i * 4 + 1, "Time"] = cur_hour.replace(minute = 15)
        df_pv.at[i * 4 + 2, "Time"] = cur_hour.replace(minute = 30)
        df_pv.at[i * 4 + 3, "Time"] = cur_hour.replace(minute = 45)

        df_pv.at[i * 4, "pv"] = nodes[i]
        df_pv.at[i * 4 + 1, "pv"] = max(nodes[i] + gradients[i] / 4, 0)
        df_pv.at[i * 4 + 2, "pv"] = max(nodes[i+1] - gradients[i+1] / 2, 0)
        df_pv.at[i * 4 + 3, "pv"] = max(nodes[i+1] - gradients[i+1] / 4, 0)

    df_pv.to_csv(config.PV_PATH, index = True, sep = ";")

    pv_before = sum(nodes)
    pv_after = 0.25 * sum(df_pv["pv"])
    print(f"overall pv generation: {pv_before}")
    print(f"pv generation from interpolation: {pv_after}")
    print(f"absolute error: {np.abs(pv_after - pv_before)}")
    print(f"relative error: {100 * np.abs(1 - pv_after / pv_before)} %")

    plt.figure(figsize = (20, 10))
    plt.plot(df_pv["pv"], marker = "o", markersize = 4)
    x_values = [4*i for i in range(len(nodes))]
    plt.plot(x_values, nodes, marker = "o", markersize = 4)
    plt.axhline(y = 0, color = "red", linestyle = "dashed")
    plt.savefig(config.OUTPUT_PATH / "pv_plot.png")

if __name__ == "__main__":
    computePVData()