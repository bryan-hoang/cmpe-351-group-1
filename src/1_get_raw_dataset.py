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

# %% [python]
# Access environment variables.
from os import environ

# Cryptocompare API
import cryptocompare

# Manipulating the raw data to save it in a ``.csv`` files.
import pandas as pd

# Loading environment variables from a `.env` file.
from dotenv import load_dotenv

# Twython API.
from twython import Twython

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
cryptocompare.get_price("BTC", currency="USD")

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
