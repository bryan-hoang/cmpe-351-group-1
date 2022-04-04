# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Predictor

# %%
import os
from datetime import timedelta

import pandas as pd
from tensorflow import keras

# %% pycharm={"name": "#%%\n"}
# os.chdir("src") used to reset to original working directory

# %% pycharm={"name": "#%%\n"}
model = keras.Sequential()
model.add(keras.layers.LSTM(8, input_shape=(3, 1)))
model.add(keras.layers.Dense(1))
model.summary()

# %% pycharm={"name": "#%%\n"}
# Used to go out into the cmpe-351-group-1 folder to access the data without
# changing directories multiple times/
os.chdir("../")

# %% pycharm={"name": "#%%\n"}
model.compile(
    loss="mean_squared_error", optimizer="adam", metrics=["mean_squared_error"]
)

# %% pycharm={"name": "#%%\n"}
crypto_dict = {
    "bitcoin": "btc",
    "avalanche": "avax",
    "doge": "doge",
    "ethereum": "eth",
    "solana": "sol",
}


# %% pycharm={"name": "#%%\n"}
def get_dataset(crypto):
    twitter_df = pd.read_csv(f"data/processed/twitter/{crypto}_sentiment.csv")
    bit_prices = pd.read_csv(
        f"data/raw/crypto/"
        f"{crypto_dict[crypto]}_2022_03_05-2022_03_11_minute.csv"
    )
    bit_prices["time"] = pd.to_datetime(bit_prices["time"], unit="s")
    price_dict = bit_prices.set_index("time")["open"].to_dict()
    twitter_df["created_at"] = twitter_df["created_at"].apply(
        lambda x: pd.to_datetime(x[:-6])
    )
    twitter_df["created_at"] = twitter_df["created_at"].apply(
        lambda x: x.replace(second=0)
    )
    twitter_df["future_date"] = twitter_df["created_at"].apply(
        lambda x: x + timedelta(hours=1)
    )
    twitter_df = twitter_df[
        twitter_df["future_date"].isin(bit_prices["time"])
    ]  # Filter out dates for which we don't have price data
    twitter_df["price"] = twitter_df["created_at"].apply(
        lambda x: price_dict[x]
    )
    twitter_df["future_price"] = twitter_df["created_at"].apply(
        lambda x: price_dict[x + timedelta(hours=1)]
    )
    X = twitter_df[["retweet_count", "vader_sentiment_compound", "price"]]
    y = twitter_df["future_price"]
    return X, y


# %% pycharm={"name": "#%%\n"}
X, y = get_dataset("avalanche")

# %% pycharm={"name": "#%%\n"}
model.fit(X, y, epochs=2000, batch_size=10)

# %% pycharm={"name": "#%%\n"}
X, y = get_dataset("bitcoin")
model.fit(X, y, epochs=2000, batch_size=10)

# %% pycharm={"name": "#%%\n"}
X, y = get_dataset("doge")
model.fit(X, y, epochs=1000, batch_size=10)

# %% pycharm={"name": "#%%\n"}
X, y = get_dataset("ethereum")
model.fit(X, y, epochs=1000, batch_size=10)

# %% pycharm={"name": "#%%\n"}
X, y = get_dataset("solana")
model.fit(X, y, epochs=1000, batch_size=10)
