import config

import pandas as pd
import datetime as dt

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

    # read and preprocess temperature data
    df_t_raw = pd.read_csv(config.TEMPERATURE_PATH, sep = ";")
    df_t = pd.DataFrame(df_t_raw, columns=["MESS_DATUM", "TT_TU"])
    for i in range(len(df_t)):
        df_t.at[i, "Time"] = dt.datetime.strptime(str(df_t["MESS_DATUM"][i]), "%Y%m%d%H")
    df_t.drop(columns = ["MESS_DATUM"], inplace = True)
    df_t.rename(columns={"TT_TU": "temperature"}, inplace=True)

    if(len(df_t) != len(df_r)):
        print(f"ERROR: radiation ({len(df_r)}) and temperature ({len(df_t)}) data do not match in length")
        return
    hours = len(df_t)
    
    df_pv = pd.DataFrame(columns = ["Time", "pv"])
    # constants for pv computation
    NOCT_T = 47                     # C     Nominal operating temperature
    P     = 44000                   # W     Maximum power at STC
    LAMB  = 0.00048                 # C^-1  Temperature coefficient (war 0.004 in BA)
    T2    = 25                      # C     Temperature at STC
    G     = 1000                    # W/m^2 Radiation at STC

    # compute hourly pv data
    for i in range(hours):
        temp = df_t["temperature"][i]   # C     Air temperature
        rad = df_r["radiation"][i]      # W/m^2 Radiation

        t1    = float(temp + (NOCT_T - 20)*(rad/800))        # C     Temperature of solar panel

        df_pv.at[i * 4, "pv"] = float((P * rad * (1-LAMB*(t1-T2)))/(G*1000)) # kWh!

        cur_hour = dt.datetime.strptime(str(df_t["Time"][i]), "%Y-%m-%d %H:%M:%S")
        df_pv.at[i * 4, "Time"] = cur_hour
        df_pv.at[i * 4 + 1, "Time"] = cur_hour.replace(minute = 15)
        df_pv.at[i * 4 + 2, "Time"] = cur_hour.replace(minute = 30)
        df_pv.at[i * 4 + 3, "Time"] = cur_hour.replace(minute = 45)
    
    # fill the quarter-hourly gaps through interpolation
    # TODO implement cubic spline interpolation (Hermite polynomials)
    for i in range(hours):
        base = df_pv["pv"][i * 4]

        df_pv.at[i * 4, "pv"] = base / 4
        df_pv.at[i * 4 + 1, "pv"] = base / 4
        df_pv.at[i * 4 + 2, "pv"] = base / 4
        df_pv.at[i * 4 + 3, "pv"] = base / 4

    df_pv.to_csv(config.PV_PATH, index = True, sep = ";")

if __name__ == "__main__":
    computePVData()
