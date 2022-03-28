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

# %%
from datetime import datetime, timedelta

# Resolving paths in a platform agnostic way.
from os.path import dirname, join, realpath

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Manipulating the raw data to save it in a ``.csv`` files.
from pandas import DataFrame, DatetimeIndex
from pandas import concat as concat_df
from pandas import date_range


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
        )
    )

    temp_dataframe["time"] = temp_dataframe["time"].transform(
        datetime.fromtimestamp
    )

    temp_dataframe["cryptocurrency"] = cryptocurrency
    prices_dataframe = pd.concat([prices_dataframe, temp_dataframe])

prices_dataframe.head()

# %%
NUM_DAYS = 7
# Decided based on limitations of API at the time of data collection.
LAST_DAY = datetime(2022, 3, 11)
DATE_RANGE = date_range(end=LAST_DAY, periods=NUM_DAYS)

tweets_dataframe = pd.DataFrame()

for date in DATE_RANGE:
    temp_dataframe = pd.read_csv(
        join(
            DATA_DIR,
            "raw",
            "twitter",
            f"tweets-{date.strftime('%Y-%m-%d')}.csv",
        )
    )

    temp_dataframe["created_at"] = pd.to_datetime(temp_dataframe["created_at"])

    tweets_dataframe = pd.concat([tweets_dataframe, temp_dataframe])

tweets_dataframe.head()

# %%
tweets_dataframe.to_csv(
    join(
        DATA_DIR,
        "processed",
        "twitter",
        f"tweets"
        f"_{(DATE_RANGE[0]).strftime('%Y_%m_%d')}"
        f"-{DATE_RANGE[-1].strftime('%Y_%m_%d')}.csv",
    )
)

# %%
