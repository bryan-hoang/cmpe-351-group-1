# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3.10.3 ('cmpe-351-group-1-FuIPzgc6')
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Social Volatility: Financial Volatility

# %%
# Importing packages.
from datetime import datetime, timedelta

# Resolving paths in a platform agnostic way.
from os import path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Manipulating the raw data to save it in a ``.csv`` files.
from pandas import DataFrame, DatetimeIndex
from pandas import concat as concat_df
from pandas import date_range


# %%
# Create and resolve paths to the data in an OS agnostic way.
def is_interactive():
    """Check if the script is being run interactively."""
    import __main__ as main

    return not hasattr(main, "__file__")


if is_interactive():
    SCRIPT_DIR = path.dirname(path.realpath("__file__"))
else:
    SCRIPT_DIR = path.dirname(path.realpath(__file__))

# "../data"
DATA_DIR = path.join(path.dirname(SCRIPT_DIR), "data")


# %%
def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return t.replace(
        second=0, microsecond=0, minute=0, hour=t.hour
    ) + timedelta(hours=t.minute // 30)


# %%
# Read in the raw cryptocurrency data.
CRYPTOCURRENCIES = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "DOGE": "doge",
    "SOL": "solana",
    "AVAX": "avalanche",
}


def load_dataset(
    cryptocurrency: str, start_date: datetime, end_date: datetime
):
    filename = path.join(
        DATA_DIR,
        "raw",
        "crypto",
        f"{cryptocurrency.lower()}_{start_date.strftime('%Y_%m_%d')}"
        f"-{end_date.strftime('%Y_%m_%d')}_minute.csv",
    )
    crypto_df = pd.read_csv(filename, index_col=0)
    crypto_df = crypto_df[["time", "open"]].rename({"open": "price"}, axis=1)
    crypto_df["time"] = crypto_df["time"].transform(datetime.fromtimestamp)
    crypto_df["cryptocurrency"] = cryptocurrency

    return crypto_df


start_date = datetime(2022, 3, 5)
end_date = datetime(2022, 3, 11)
btc_prices = load_dataset("BTC", start_date, end_date)
btc_prices.head()


# %%
def calculate_returns(prices: DataFrame):
    prices["minutely_return"] = np.log(prices["price"].pct_change() + 1)
    return prices


btc_prices = calculate_returns(btc_prices)
btc_prices.head()


# %%
def calculate_financial_volatility(prices: DataFrame):
    """Calculate the minutely volatility"""
    prices["minutely_volatility"] = prices["minutely_return"].rolling(
        window=2
    ).std() * np.sqrt(2)
    return prices


btc_prices = calculate_financial_volatility(btc_prices)
btc_prices.head()


# %%
def transform_data_through_pipeline(prices: DataFrame):
    """Transform the data through the pipeline"""
    return prices.pipe(calculate_returns).pipe(calculate_financial_volatility)


btc_prices = transform_data_through_pipeline(btc_prices)
btc_prices.head()


# %%
def get_financial_volatilitys(
    cryptocurrency: str, start_date: datetime, end_date: datetime
):
    """Calculate the financial volatility for all cryptocurrencies"""
    crypto_df = load_dataset(cryptocurrency, start_date, end_date)
    crypto_df = transform_data_through_pipeline(crypto_df)
    return crypto_df


# %%
def append_financial_volatilities(start_date: datetime, end_date: datetime):
    """Append the financial volatility for all cryptocurrencies"""
    global btc_prices, eth_prices, doge_prices, sol_prices, avax_prices
    btc_prices = pd.concat(
        [btc_prices, get_financial_volatilitys("BTC", start_date, end_date)]
    )
    eth_prices = pd.concat(
        [eth_prices, get_financial_volatilitys("ETH", start_date, end_date)]
    )
    doge_prices = pd.concat(
        [doge_prices, get_financial_volatilitys("DOGE", start_date, end_date)]
    )
    sol_prices = pd.concat(
        [sol_prices, get_financial_volatilitys("SOL", start_date, end_date)]
    )
    avax_prices = pd.concat(
        [avax_prices, get_financial_volatilitys("AVAX", start_date, end_date)]
    )


# %%
btc_prices = DataFrame()
eth_prices = DataFrame()
doge_prices = DataFrame()
sol_prices = DataFrame()
avax_prices = DataFrame()

start_date = datetime(2022, 3, 5)
end_date = datetime(2022, 3, 11)

append_financial_volatilities(start_date, end_date)

start_date = datetime(2022, 3, 28)
end_date = datetime(2022, 4, 4)

append_financial_volatilities(start_date, end_date)

print(btc_prices.head())
print(btc_prices.tail())


# %%
def floor_minute(t: datetime):
    """Floor the minute of a datetime."""
    return t.replace(second=0, microsecond=0)


def sync_twitter_and_crypto_data(cryptocurrency, crypto_df):
    financial_volatility_and_sentiment_df = DataFrame()
    twitter_df = pd.read_csv(
        path.join(
            DATA_DIR,
            "processed",
            "twitter",
            f"{CRYPTOCURRENCIES[cryptocurrency]}_sentiment.csv",
        ),
        index_col=0,
    )
    twitter_df = twitter_df[["created_at", "vader_sentiment_compound"]].rename(
        {"created_at": "time", "vader_sentiment_compound": "sentiment"}, axis=1
    )

    price_dict = crypto_df.set_index("time")["price"].to_dict()

    twitter_df["time"] = twitter_df["time"].transform(
        lambda x: pd.to_datetime(x).tz_localize(None)
    )
    twitter_df["time"] = twitter_df["time"].transform(floor_minute)
    crypto_df["time"] = crypto_df["time"].transform(floor_minute)

    financial_volatility_and_sentiment_df = crypto_df.merge(
        twitter_df, on="time"
    ).drop_duplicates()

    financial_volatility_and_sentiment_df = (
        financial_volatility_and_sentiment_df[
            financial_volatility_and_sentiment_df["sentiment"].notna()
        ]
    )

    return financial_volatility_and_sentiment_df


financial_volatility_and_sentiment_df = sync_twitter_and_crypto_data(
    "BTC", btc_prices
)
print(len(financial_volatility_and_sentiment_df))
print(financial_volatility_and_sentiment_df.head())
print(financial_volatility_and_sentiment_df.tail())

# %%
btc_social_volitility = abs(
    financial_volatility_and_sentiment_df[
        ["minutely_volatility", "sentiment"]
    ].corr(method="pearson")["minutely_volatility"]["sentiment"]
)
btc_social_volitility


# %%
def get_social_volitility(cryptocurrency, crypto_df):
    financial_volatility_and_sentiment_df = sync_twitter_and_crypto_data(
        cryptocurrency, crypto_df
    )
    return abs(
        financial_volatility_and_sentiment_df[
            ["minutely_volatility", "sentiment"]
        ].corr(method="pearson")["minutely_volatility"]["sentiment"]
    )


eth_social_volitility = get_social_volitility("ETH", eth_prices)
doge_social_volitility = get_social_volitility("DOGE", doge_prices)
sol_social_volitility = get_social_volitility("SOL", sol_prices)
avax_social_volitility = get_social_volitility("AVAX", avax_prices)

# %%
social_volatilities_df = pd.DataFrame(
    {
        "crypcocurrency": ["BTC", "ETH", "DOGE", "SOL", "AVAX"],
        "social_volatility": [
            btc_social_volitility,
            eth_social_volitility,
            doge_social_volitility,
            sol_social_volitility,
            avax_social_volitility,
        ],
    }
)
social_volatilities_df = social_volatilities_df.sort_values(
    by="social_volatility", ascending=False
).reset_index(drop=True)
social_volatilities_df.head()

# %%
sns.barplot(
    x="social_volatility", y="crypcocurrency", data=social_volatilities_df
)
