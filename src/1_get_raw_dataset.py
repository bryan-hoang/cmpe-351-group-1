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
# # Getting the raw dataset
#
# We'll be using `twython` and `cryptocompare` as APIs to get the respective
# Twitter and cryptocurrency data that will make up the project's dataset.
#
# ## Importing packages.
#
# First, we'll import the necessary python packages.
#

# %% [python]
from datetime import datetime

# Access environment variables.
from os import environ

# Resolving paths in a platform agnostic way.
from os.path import dirname, join, realpath

# Cryptocompare API.
from cryptocompare import get_historical_price_minute, get_price

# Loading environment variables from a `.env` file.
from dotenv import load_dotenv

# Manipulating the raw data to save it in a ``.csv`` files.
from pandas import DataFrame

# Twython API.
from twython import Twython


# %%
def is_interactive():
    import __main__ as main

    return not hasattr(main, "__file__")


if is_interactive():
    SCRIPT_DIR = dirname(realpath("__file__"))
else:
    SCRIPT_DIR = dirname(realpath(__file__))

DATA_DIR = join(dirname(SCRIPT_DIR), "data")

# %% [markdown]
# ## Loading secrets from environment variables.
#
# Next, we need to set credentials to access the CryptoCompare and Twython
# APIs. To avoid hard coding the secrets, we'll load them from the environment,
# i.e., a `.env` file.

# %%
# Loads environment variables from a `.env` file.
load_dotenv()

# Now the environment variables from the file are available, as if they were
# specified typically from the commandline.
TWITTER_APP_KEY = environ["TWITTER_APP_KEY"]
TWITTER_APP_SECRET = environ["TWITTER_APP_SECRET"]

# %% [markdown]
# ## Testing the APIs.
#
# Let's test the CryptoCompare API. `CRYPTOCOMPARE_API_KEY` should be specified
# in the `.env` file so that the python package can detect it automatically as
# an environment variable.

# %%
get_price("BTC", currency="USD")

# %% [markdown]
# Now let's test accessing Twitter's API through Twython.

# %%
twitter = Twython(TWITTER_APP_KEY, TWITTER_APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter = Twython(
    TWITTER_APP_KEY, TWITTER_APP_SECRET, access_token=ACCESS_TOKEN
)

search_results = twitter.search(count=1, q="cryptocurrency")
print(search_results)

# %% [markdown]
# ## Getting cryptocurrency data

# %%
cryptocurrencies = ["BTC", "ETH", "DOGE", "SOL", "AVAX"]
for cryptocurrency in cryptocurrencies:
    price_dataset = []
    earliest_timestamp = datetime.now()
    days_count = 7
    for day in range(0, days_count):
        price_dataset += get_historical_price_minute(
            cryptocurrency, "USD", limit=1440, toTs=earliest_timestamp
        )

        earliest_timestamp = price_dataset[-1]["time"]

    # Saving the raw price data to a csv file.
    price_data_frame = DataFrame(price_dataset)
    price_data_frame.to_csv(
        join(
            DATA_DIR,
            "raw",
            "crypto",
            f"{cryptocurrency.lower()}_{days_count}_days_by_minute.csv",
        )
    )
