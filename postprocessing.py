import matplotlib.pyplot as plt
import config
import scenario


def bar_chart(df, sc : scenario.Scenario):
    last_row = df.iloc[-1]
    # Extract the values for the desired columns
    offer_DA = last_row["offer_DA"]
    offer_IA = last_row["offer_IA"]
    offer_IC = last_row["offer_IC"]
    grid_supply = last_row["grid_feedin"]
    grid_demand = last_row["costs"]
    colors = ["steelblue", "lightsteelblue", "lightslategray", "slategray", "red"]
    columns = ["Day Ahead", "Intraday Auction", "Intraday Continuous", "Grid_supply", "Grid_demand"]
    values = [offer_DA, offer_IA, offer_IC, grid_supply, grid_demand]
    plt.bar(columns, values, color=colors)
    plt.xlabel("Offered Markets", labelpad=10)
    plt.ylabel("Gains in €", labelpad=10)
    plt.title("Scenario 1: Cumulated Gains")
    plt.xticks(fontsize=8)
    print(f"cumulated gains for IC: {offer_IC}")
    print(f"cumulated gains for IA: {offer_IA}")
    print(f"cumulated gains for DA: {offer_DA}")
    print(f"cumulated gains for Grid: {grid_supply}")
    print(f"cumulated gains for whole scenario: {offer_IC+offer_IA+offer_DA+grid_supply-grid_demand}")
    # path = config.OUTPUT_PATH / (sc.name + "_bar_chart.png")
    # plt.savefig(path)

    plt.show()


def line_chart(df, sc : scenario.Scenario):
    columns = ["offer_DA", "offer_IA", "offer_IC", "grid_feedin"]
    y_values = df[columns]
    y_values = y_values.rename(
        columns={"offer_DA": "Day Ahead", "offer_IA": "Intraday Auction", "offer_IC": "Intraday Continuous",
                 "grid_feedin": "Grid"})
    x_values = df["Time"]
    colors = ["steelblue", "lightsteelblue", "lightslategray", "slategray"]
    plt.subplots_adjust(bottom=0.2)  # Adjust the bottom parameter to decrease the height
    for i, column in enumerate(y_values.columns):
        plt.plot(x_values, y_values[column], color=colors[i])
    plt.xlabel("Time", labelpad=10)
    plt.ylabel("Gains in €", labelpad=10)
    plt.title("Scenario 1: Cumulated Gains")
    plt.legend(title="Offered Markets", labels=y_values)
    plt.xticks(rotation=45)

    # path = config.OUTPUT_PATH / (sc.name + "_line_chart.png")
    # plt.savefig(path)

    plt.show()


def fancy_chart(df, sc : scenario.Scenario):
    df["Offer"] = df["Quantity"] * df["Price"]
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 4))  # Set the figure size as 10 inches wide and 4 inches tall
    colors = {'DA':  "steelblue", 'IA': "teal", 'IC': "purple"}
    # Plotting bars with different colors based on the 'Market' column
    for i, row in df.iterrows():
        market = row['Market']
        color = colors.get(market, 'gray')  # Use gray color if market not found in colors dictionary
        ax.bar(i, row['Offer'], color=color)

    ax.set_xlabel('Time')
    ax.set_ylabel('Gains in €')
    ax.set_title('Scenario 1: Placed offers')
    ax.spines['top'].set_visible(False)  # Remove the top border
    ax.spines['right'].set_visible(False)  # Remove the right border
    ax.spines['bottom'].set_visible(False)  # Remove the bottom border
    ax.spines['left'].set_visible(False)  # Remove the left border

    # path = config.OUTPUT_PATH / (sc.name + "_fancy_chart.png")
    # plt.savefig(path)

    plt.show()


def battery_chart(df, sc : scenario.Scenario):
    battery_charge_data = df['battery_charge'].tolist()
    time_data = df['Time'].tolist()

    fig, ax = plt.subplots(figsize=(12, 4))
    # Plot the line chart
    ax.plot(time_data, battery_charge_data, linestyle='-', color='b', linewidth=0.2)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)  # Remove the top border
    ax.spines['right'].set_visible(False)  # Remove the right border
    ax.spines['bottom'].set_visible(False)  # Remove the bottom border
    ax.spines['left'].set_visible(False)  # Remove the left border

    # Adjust the bottom parameter to decrease the height
    plt.subplots_adjust(bottom=0.4)

    # Add labels and title to the plot
    plt.xlabel('Time')
    plt.ylabel('Battery Charge')
    plt.title('Battery Charge State')
    plt.xticks(rotation=45)

    # Show the plot
    plt.show()


def show_charge(df, sc : scenario.Scenario):
    df['charge_update'] = df['battery_charge'].diff()
    df['charge_update'].fillna(0, inplace=True)
    # Create a new column 'color' based on the sign of 'charge_update'
    df['color'] = df['charge_update'].apply(lambda x: 'green' if x > 0 else 'red' if x < 0 else 'black')
    # Calculate the moving average over a window of 30 timesteps
    window_size = 30
    df['moving_average'] = df['battery_charge'].rolling(window=window_size).mean()
    # Convert the 'charge_update' and 'Time' columns to lists
    battery_charge_data = df['charge_update'].tolist()
    time_data = df.index.tolist()
    # Create the plot
    plt.subplots(figsize=(12, 4))
    plt.bar(time_data, battery_charge_data, color=df['color'])
    # Plot the moving average line
    plt.plot(time_data, df['moving_average'], color='blue', linewidth=0.5)
    # Adjust the bottom parameter to decrease the height
    plt.subplots_adjust(bottom=0.4)
    # Add labels and title to the plot
    plt.xlabel('Index')
    plt.ylabel('Battery Charge')
    plt.title('Battery Charge State with Moving Average (Window Size: {})'.format(window_size))
    plt.xticks(rotation=45)

    # path = config.OUTPUT_PATH / (sc.name + "_charge.png")
    # plt.savefig(path)

    # Show the plot
    plt.show()


def demand_line(df, sc : scenario.Scenario):
    columns = ["pv", "load", "battery_charge"]
    y_values = df[columns]
    x_values = df["Time"]
    colors = ["#005b96", "#00a8e8", "#333333"]

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Plot the first two columns on the left y-axis
    ax1.plot(x_values, y_values.iloc[:, 0], color=colors[0], linewidth=0.8, label="pv")
    ax1.plot(x_values, y_values.iloc[:, 1], color=colors[1], linewidth=0.8, label="load")

    # Plot the third column on the right y-axis
    ax2.plot(x_values, y_values.iloc[:, 2], color=colors[2], linewidth=0.8, label="battery_charge")

    ax1.set_xlabel("Time", labelpad=10)
    ax1.set_ylabel("kWh", labelpad=10)
    ax2.set_ylabel("kWh", labelpad=10)

    # Fill the area under the chart when "load" is bigger than "pv"
    ax1.fill_between(x_values, y_values.iloc[:, 0], y_values.iloc[:, 1],
                     where=(y_values.iloc[:, 1] > y_values.iloc[:, 0]),
                     interpolate=True, color='lightblue', alpha=0.5)

    # Set the title and rotate the x-axis labels
    plt.title("Scenario 1: Residential Profil")
    ax1.tick_params(axis='x', rotation=45)
    plt.subplots_adjust(bottom=0.3)

    # Save the graph as a high-resolution image
    # path = config.OUTPUT_PATH / (sc.name + "_demand_line.png")
    # plt.savefig(path, dpi=1200)

    plt.show()


def demand_line1(df, sc : scenario.Scenario):
    columns = ["pv", "load"]
    y_values = df[columns]
    x_values = df["Time"]
    colors = ["#005b96", "#00a8e8"]

    fig, ax = plt.subplots(figsize=(12, 4))  # Adjust the figsize to change the width and height

    ax.fill_between(x_values, y_values.iloc[:, 0], y_values.iloc[:, 1],
                     where=(y_values.iloc[:, 1] > y_values.iloc[:, 0]),
                     interpolate=True, color='lightblue', alpha=0.5)

    for i, column in enumerate(y_values.columns):
        ax.plot(x_values, y_values[column], color=colors[i], linewidth=0.8)

    ax.set_xlabel("Time", labelpad=10)
    ax.set_ylabel("kWh", labelpad=10)
    ax.set_title("Scenario 1: Residential Profil")
    ax.tick_params(axis='x', rotation=45)
    plt.subplots_adjust(bottom=0.3)
    ax.spines['top'].set_visible(False)  # Remove the top border
    ax.spines['right'].set_visible(False)  # Remove the right border
    ax.spines['bottom'].set_visible(False)  # Remove the bottom border
    ax.spines['left'].set_visible(False)  # Remove the left border

    # Save the graph as a high-resolution image
    # path = config.OUTPUT_PATH / (sc.name + "_demand_line1.png")
    # plt.savefig(path, dpi=1200)  # Adjust the file name and dpi value as needed

    plt.show()


def price_line1(df, sc : scenario.Scenario):
    columns = ["costs", "grid_feedin", "offer_DA", "offer_IA", "offer_IC"]
    y_values = df[columns]
    x_values = df["Time"]
    colors = ["red", "green", "steelblue", "teal", "purple" ]
    fig, ax = plt.subplots(figsize=(12, 5))  # Adjust the figsize to change the width and height
    for i, column in enumerate(y_values.columns):
        ax.plot(x_values, y_values[column], color=colors[i], linewidth=0.8)
    ax.set_xlabel("Time", labelpad=10)
    ax.set_ylabel("cumulated Gains/losses in €", labelpad=10)
    ax.tick_params(axis='x', rotation=45)
    plt.subplots_adjust(bottom=0.3)
    plt.legend(labels=y_values)
    ax.spines['top'].set_visible(False)  # Remove the top border
    ax.spines['right'].set_visible(False)  # Remove the right border
    ax.spines['bottom'].set_visible(False)  # Remove the bottom border
    ax.spines['left'].set_visible(False)  # Remove the left border

    # Save the graph as a high-resolution image
    # path = config.OUTPUT_PATH / (sc.name + "_price_line1.png")
    # plt.savefig(path, dpi=1200)  # Adjust the file name and dpi value as needed

    plt.show()


def counter(df):
    DA = 0
    IA = 0
    IC = 0

    for i in df["Market"]:
        if i == "IC":
            IC +=1
        elif i == "DA":
            DA += 1
        elif i == "IA":
            IA += 1
    sum_quantity_IC = df[df["Market"] == "IC"]["Quantity"].sum()
    sum_quantity_IA = df[df["Market"] == "IA"]["Quantity"].sum()
    sum_quantity_DA = df[df["Market"] == "DA"]["Quantity"].sum()
    print(f"DA: {DA}")
    print(f"IA: {IA}")
    print(f"IC: {IC}")
    print(f"IC_Q: {sum_quantity_IC}")
    print(f"IA_Q: {sum_quantity_IA}")
    print(f"DA_Q: {sum_quantity_DA}")
    print(f"Spot Market offer: {DA+IA+IC}")
    print(f"Grid: {33792-DA-IA-IC}")
