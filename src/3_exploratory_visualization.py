# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3.10.0 ('cmpe-351-group-1-FuIPzgc6')
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Exploratory visualization

# %%
from datetime import datetime

# Resolving paths in a platform agnostic way.
from os.path import dirname, join, realpath

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Manipulating the raw data to save it in a ``.csv`` files.
from pandas import DataFrame, DatetimeIndex


# %%
def is_interactive():
    """Check if the script is being run interactively."""
    import __main__ as main

    return not hasattr(main, "__file__")


if is_interactive():
    SCRIPT_DIR = dirname(realpath("__file__"))
else:
    SCRIPT_DIR = dirname(realpath(__file__))

# "../data"
DATA_DIR = join(dirname(SCRIPT_DIR), "data")

# %% [markdown]
# ## Graphing Cryptocurrency prices

# %%
CRYPTOCURRENCIES = [
    "BTC",
    "ETH",
    "DOGE",
    "SOL",
    "AVAX",
]

prices_dataframe = pd.DataFrame()

for cryptocurrency in CRYPTOCURRENCIES:
    temp_dataframe = pd.read_csv(
        join(
            DATA_DIR,
            "raw",
            "crypto",
            f"{cryptocurrency.lower()}_2022_03_05-2022_03_11_minute.csv",
        ),
        # Number of minutes in an hour + header row.
        nrows=61,
    )

    temp_dataframe["time"] = temp_dataframe["time"].transform(
        datetime.fromtimestamp
    )

    temp_dataframe["cryptocurrency"] = cryptocurrency
    prices_dataframe = pd.concat([prices_dataframe, temp_dataframe])

prices_dataframe.head()

# %%
btc_price_dataframe = prices_dataframe[
    prices_dataframe["cryptocurrency"] == "BTC"
]

fig, ax = plt.subplots()

ax.plot(btc_price_dataframe["time"], btc_price_dataframe["open"])

x_formatter = mdates.DateFormatter("%H:%M")
ax.xaxis.set_major_formatter(x_formatter)

ax.set_xlabel("Time (H:M)")
ax.set_ylabel("Price (USD)")
ax.set_title("The price of Bitcoin over an hour on March 4th")

plt.show()

# %%
# Create a grid : initialize it
g = sns.FacetGrid(
    prices_dataframe, col="cryptocurrency", hue="cryptocurrency", col_wrap=3
)

# Add the line over the area with the plot function
g = g.map(plt.plot, "time", "open")

# Fill the area with fill_between
g = g.map(plt.fill_between, "time", "open", alpha=0.2).set_titles(
    "{col_name} cryptocurrency"
)

# Control the title of each facet
g.set_titles("{col_name}")

g.set_axis_labels("Time (H:M)", "Price (USD)")
g.fig.subplots_adjust(top=0.85)
g.fig.suptitle("The prices of cryptocurrencies over an hour on March 4th")

xformatter = mdates.DateFormatter("%H:%M")

# iterate over axes of FacetGrid
for ax in g.axes.flat:
    labels = ax.get_xticklabels()  # get x labels
    ax.set_xticklabels(labels, rotation=30)  # set new labels
    ax.xaxis.set_major_formatter(xformatter)

# Add a title for the whole plot
# plt.subplots_adjust(top=0.92)
# g = g.fig.suptitle("Evolution of the value of stuff in 16 countries")

# Show the graph
plt.show()
