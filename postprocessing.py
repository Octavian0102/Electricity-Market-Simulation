import config

import matplotlib.pyplot as plt


def post_bar(df):
    last_row = df.iloc[-1]
    # Extract the values for the desired columns
    offer_DA = last_row["offer_DA"]
    offer_IA = last_row["offer_IA"]
    offer_IC = last_row["offer_IC"]
    grid_supply = last_row["grid_feedin"]
    colors = ["steelblue", "lightsteelblue", "lightslategray", "slategray"]
    columns = ["Day Ahead", "Intraday Auction", "Intraday Continuous", "Grid"]
    values = [offer_DA, offer_IA, offer_IC, grid_supply]
    plt.bar(columns, values, color=colors)
    plt.xlabel("Offered Markets", labelpad=10)
    plt.ylabel("Gains in €", labelpad=10)
    plt.title("Scenario 1: Cumulated Gains")
    plt.xticks(fontsize=8)
    plt.savefig(config.OUTPUT_PATH / "bar_chart.png")
    plt.show()


def line_chart(df):
    columns = ["offer_DA", "offer_IA", "offer_IC", "grid_feedin"]
    y_values = df[columns]
    y_values = y_values.rename(columns={"offer_DA": "Day Ahead", "offer_IA": "Intraday Auction", "offer_IC": "Intraday Continuous",
                       "grid_feedin": "Grid"})
    x_values = df["Time"]
    colors = ["steelblue", "lightsteelblue", "lightslategray", "slategray"]
    for i, column in enumerate(y_values.columns):
        plt.plot(x_values, y_values[column], color=colors[i])
    plt.xlabel("Time", labelpad=10)
    plt.ylabel("Gains in €", labelpad=10)
    plt.title("Scenario 1: Cumulated Gains")
    plt.legend(title="Offered Markets", labels=columns)
    plt.xticks(rotation=45)
    plt.savefig(config.OUTPUT_PATH / "line_chart.png")
    plt.show()


def fancy_chart(df):
    plt.figure(figsize = (20, 10))
    plt.plot(df["battery_charge"], marker = "o", markersize = 4)
    plt.plot(df["pv"], marker = "o", markersize = 4)
    plt.axhline(y = 0, color = "red", linestyle = "dashed")
    plt.axhline(y = 100, color = "red", linestyle = "dashed")
    plt.savefig(config.OUTPUT_PATH / "fancy_chart.png")