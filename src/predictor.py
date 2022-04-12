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
from datetime import datetime, timedelta

import keras
import numpy as np
import pandas as pd

# %% pycharm={"name": "#%%\n"}
# os.chdir("src") #used to reset to original working directory

# %% pycharm={"name": "#%%\n"}
os.chdir(
    "../"
)  # Used to go out into the cmpe-351-group-1 folder to access the data without changing directories multiple times


# %% pycharm={"name": "#%%\n"}
def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return t.replace(
        second=0, microsecond=0, minute=0, hour=t.hour
    ) + timedelta(hours=t.minute // 30)


# %% pycharm={"name": "#%%\n"}
def normalize(df, column):
    m = df[column].mean()
    s = df[column].std()
    df[column] = df[column].apply(lambda x: (x - m) / s)
    return df[column]


# %% pycharm={"name": "#%%\n"}
##Dates is an array of tuples consisting of month and day as numbers
def get_dataset(crypto, start_month, start_day, end_month, end_day):
    twitter_df = pd.read_csv(f"data/processed/twitter/{crypto}_sentiment.csv")
    try:
        crypt_prices = pd.read_csv(
            f"data/raw/crypto/{crypto_dict[crypto]}_2022_{start_month}_{start_day}-2022_{end_month}_{end_day}_minute.csv"
        )
    except:
        crypt_prices = pd.read_csv(
            f"data/raw/crypto/{crypto_dict[crypto]}_2022_{start_month}_{start_day}-2022_{end_month}_{end_day}.csv"
        )
    crypt_prices["time"] = pd.to_datetime(crypt_prices["time"], unit="s")
    price_dict = crypt_prices.set_index("time")["open"].to_dict()
    twitter_df["created_at"] = twitter_df["created_at"].apply(
        lambda x: pd.to_datetime(x).tz_localize(None)
    )
    twitter_df["created_at"] = twitter_df["created_at"].apply(
        lambda x: hour_rounder(x)
    )
    twitter_df["future_date"] = twitter_df["created_at"].apply(
        lambda x: x + timedelta(hours=23)
    )

    twitter_df = twitter_df[
        twitter_df["future_date"].isin(crypt_prices["time"])
    ]  ##Filter out dates for which we don't have price data

    # print(len(twitter_df))

    twitter_df = twitter_df[
        twitter_df["created_at"].isin(crypt_prices["time"])
    ]  ##Filter out dates for which we don't have price data

    twitter_df["price"] = twitter_df["created_at"].apply(
        lambda x: price_dict[x]
    )
    for i in range(1, 24):
        twitter_df[f"price_{i}hours"] = twitter_df["created_at"].apply(
            lambda x: price_dict[x + timedelta(hours=i)]
        )
    twitter_df["retweet_count"] = normalize(twitter_df, "retweet_count")
    twitter_df["favourite_count"] = normalize(twitter_df, "retweet_count")
    twitter_df["followers_count"] = normalize(twitter_df, "retweet_count")
    twitter_df["authority"] = twitter_df[
        ["retweet_count", "favourite_count", "followers_count"]
    ].sum(axis=1)

    X = twitter_df[["authority", "vader_sentiment_compound", "price"]]
    y = twitter_df[[f"price_{i}hours" for i in range(1, 24)]]
    return twitter_df, X, y


# %% pycharm={"name": "#%%\n"}
def make_model(n=3):
    model = keras.Sequential()
    model.add(keras.layers.LSTM(8, input_shape=(n, 1)))
    model.add(keras.layers.Dense(32))
    model.add(keras.layers.Dense(23))
    model.compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=["mean_squared_error"],
    )
    return model


# %% pycharm={"name": "#%%\n"}
def estimate_price(model, date, df):
    date_23_hours = date - timedelta(hours=23)
    date_1_hours = date - timedelta(hours=1)
    df_useful = df[
        (df["created_at"] <= date_1_hours)
        & (df["created_at"] >= date_23_hours)
    ]
    if len(df_useful) == 0:
        return ""
    else:
        df_useful["idx"] = df_useful["created_at"].apply(
            lambda x: round((date - x).seconds / 60 / 60)
        )
        X = df_useful[["authority", "vader_sentiment_compound", "price"]]
        y_hat = model.predict_on_batch(X)
        # print(y_hat)
        idx = df_useful["idx"].values
        vals = []
        for i in range(len(y_hat)):
            vals.append(y_hat[i][idx[i] - 1])
        return np.mean(vals)


# %% pycharm={"name": "#%%\n"}
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) * 24):
        yield start_date + timedelta(hours=n)


# %% pycharm={"name": "#%%\n"}
def make_prediction(start_date, end_date, model, df):
    pred = {}
    for date in daterange(
        datetime.strptime(start_date, "%d/%m/%Y"),
        datetime.strptime(end_date, "%d/%m/%Y"),
    ):
        val = estimate_price(model, date, df)
        if val != "":
            pred[date.strftime("%Y-%m-%d %H:%M:%S")] = val
    return pred


# %% pycharm={"name": "#%%\n"}
def evaluate_model(start_date, end_date, model, df_test):
    y_hat = make_prediction(start_date, end_date, model, df_test)
    df_temp = df_test.set_index("created_at")["price"].drop_duplicates()
    mse = 0
    for i in y_hat:
        try:
            mse += (df_temp.loc[i].values[0] - y_hat[i]) ** 2
        except:
            pass
    return mse / len(y_hat)


# %% pycharm={"name": "#%%\n"}
def make_time_series_dataset(
    crypto, start_month, start_day, end_month, end_day
):
    X = []
    y = []
    try:
        crypt_prices = pd.read_csv(
            f"data/raw/crypto/{crypto_dict[crypto]}_2022_{start_month}_{start_day}-2022_{end_month}_{end_day}_minute.csv"
        )

    except:
        crypt_prices = pd.read_csv(
            f"data/raw/crypto/{crypto_dict[crypto]}_2022_{start_month}_{start_day}-2022_{end_month}_{end_day}.csv"
        )

    crypt_prices["time"] = pd.to_datetime(crypt_prices["time"], unit="s")

    crypt_prices_useful = {}

    for i in crypt_prices[["time", "open"]].values:
        if int(i[0].strftime("%M")) == 0 and int(i[0].strftime("%S")) == 0:
            crypt_prices_useful[i[0]] = i[1]
    for i in crypt_prices_useful:
        if (i - timedelta(hours=23)) in crypt_prices_useful:
            X.append(
                [
                    crypt_prices_useful[i]
                    for i in pd.date_range(
                        i - timedelta(hours=23),
                        i - timedelta(hours=1),
                        freq="H",
                    )
                ]
            )
            y.append(crypt_prices_useful[i])
    return X, y


# %% pycharm={"name": "#%%\n"}
def make_ts_model():
    model = keras.Sequential()
    model.add(keras.layers.LSTM(8, input_shape=(23, 1)))
    model.add(keras.layers.Dense(32))
    model.add(keras.layers.Dense(1))
    model.compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=["mean_squared_error"],
    )
    return model


# %% pycharm={"name": "#%%\n"}
df_avax, X_avax, y_avax = get_dataset("avalanche", "03", "05", "03", "11")
df_avax2, X_avax2, y_avax2 = get_dataset("avalanche", "03", "28", "04", "04")
df_avax3, X_avax3, y_avax3 = get_dataset("avalanche", "03", "11", "03", "12")
df_avax4, X_avax4, y_avax4 = get_dataset("avalanche", "04", "04", "04", "05")

df_avax = df_avax.append(df_avax2)
df_avax = df_avax.append(df_avax3)
df_avax = df_avax.append(df_avax4)

X_avax = X_avax.append(X_avax2)
X_avax = X_avax.append(X_avax3)
X_avax = X_avax.append(X_avax4)

y_avax = y_avax.append(y_avax2)
y_avax = y_avax.append(y_avax3)
y_avax = y_avax.append(y_avax4)

df_avax_test, _, _ = get_dataset("avalanche", "04", "05", "04", "07")


# %% pycharm={"name": "#%%\n"}
df_btc, X_btc, y_btc = get_dataset("bitcoin", "03", "05", "03", "11")
df_btc2, X_btc2, y_btc2 = get_dataset("bitcoin", "03", "28", "04", "04")
df_btc3, X_btc3, y_btc3 = get_dataset("bitcoin", "03", "11", "03", "12")
df_btc4, X_btc4, y_btc4 = get_dataset("bitcoin", "04", "04", "04", "05")

df_btc = df_btc.append(df_btc2)
df_btc = df_btc.append(df_btc3)
df_btc = df_btc.append(df_btc4)

X_btc = X_btc.append(X_btc2)
X_btc = X_btc.append(X_btc3)
X_btc = X_btc.append(X_btc4)

y_btc = y_btc.append(y_btc2)
y_btc = y_btc.append(y_btc3)
y_btc = y_btc.append(y_btc4)
df_btc_test, _, _ = get_dataset("bitcoin", "04", "05", "04", "07")


# %% pycharm={"name": "#%%\n"}
df_eth, X_eth, y_eth = get_dataset("ethereum", "03", "05", "03", "11")
df_eth2, X_eth2, y_eth2 = get_dataset("ethereum", "03", "28", "04", "04")
df_eth3, X_eth3, y_eth3 = get_dataset("ethereum", "03", "11", "03", "12")
df_eth4, X_eth4, y_eth4 = get_dataset("ethereum", "04", "04", "04", "05")

df_eth = df_eth.append(df_eth2)
df_eth = df_eth.append(df_eth3)
df_eth = df_eth.append(df_eth4)


X_eth = X_eth.append(X_eth2)
X_eth = X_eth.append(X_eth3)
X_eth = X_eth.append(X_eth4)

y_eth = y_eth.append(y_eth2)
y_eth = y_eth.append(y_eth3)
y_eth = y_eth.append(y_eth4)

df_eth_test, _, _ = get_dataset("ethereum", "04", "05", "04", "07")

# %% pycharm={"name": "#%%\n"}
df_sol, X_sol, y_sol = get_dataset("solana", "03", "05", "03", "11")
df_sol2, X_sol2, y_sol2 = get_dataset("solana", "03", "28", "04", "04")
df_sol3, X_sol3, y_sol3 = get_dataset("solana", "03", "11", "03", "12")
df_sol4, X_sol4, y_sol4 = get_dataset("solana", "04", "04", "04", "05")

df_sol = df_sol.append(df_sol2)
df_sol = df_sol.append(df_sol3)
df_sol = df_sol.append(df_sol4)


X_sol = X_sol.append(X_sol2)
X_sol = X_sol.append(X_sol3)
X_sol = X_sol.append(X_sol4)

y_sol = y_sol.append(y_sol2)
y_sol = y_sol.append(y_sol3)
y_sol = y_sol.append(y_sol4)

df_sol_test, _, _ = get_dataset("solana", "04", "05", "04", "07")

# %% pycharm={"name": "#%%\n"}
df_doge, X_doge, y_doge = get_dataset("doge", "03", "05", "03", "11")
df_doge2, X_doge2, y_doge2 = get_dataset("doge", "03", "28", "04", "04")
df_doge3, X_doge3, y_doge3 = get_dataset("doge", "03", "11", "03", "12")
df_doge4, X_doge4, y_doge4 = get_dataset("doge", "04", "04", "04", "05")

df_doge = df_doge.append(df_doge2)
df_doge = df_doge.append(df_doge3)
df_doge = df_doge.append(df_doge4)


X_doge = X_doge.append(X_doge2)
X_doge = X_doge.append(X_doge3)
X_doge = X_doge.append(X_doge4)

y_doge = y_doge.append(y_doge2)
y_doge = y_doge.append(y_doge3)
y_doge = y_doge.append(y_doge4)

df_doge_test, _, _ = get_dataset("doge", "04", "05", "04", "07")

# %% pycharm={"name": "#%%\n"}
bit_model = make_model(2)
bit_model.fit(X_btc, y_btc, epochs=500, batch_size=10)

# %% pycharm={"name": "#%%\n"}
eth_model = make_model()
eth_model.fit(X_eth, y_eth, epochs=1000, batch_size=10)

# %% pycharm={"name": "#%%\n"}
doge_model = make_model()
doge_model.fit(X_doge, y_doge, epochs=1000, batch_size=10)

# %% pycharm={"name": "#%%\n"}
sol_model = make_model()
sol_model.fit(X_sol, y_sol, epochs=1000, batch_size=10)

# %% pycharm={"name": "#%%\n"}
avax_model = make_model()
avax_model.fit(X_avax, y_avax, epochs=1000, batch_size=10)

# %% pycharm={"name": "#%%\n"}
X_ts_btc, y_ts_btc = make_time_series_dataset(
    "bitcoin", "01", "03", "04", "03"
)
X_test_btc, y_test_btc = make_time_series_dataset(
    "bitcoin", "04", "05", "04", "07"
)
bit_ltsm = make_ts_model()
bit_ltsm.fit(
    X_ts_btc,
    y_ts_btc,
    epochs=500,
    batch_size=10,
    validation_data=(X_test_btc, y_test_btc),
)

# %% pycharm={"name": "#%%\n"}
evaluate_model("05/04/2022", "07/04/2022", bit_model, df_btc_test)

# %% [markdown] pycharm={"name": "#%% md\n"}
# Much better accuracy from sentiment model than just time series

# %% pycharm={"name": "#%%\n"}
X_ts_eth, y_ts_eth = make_time_series_dataset(
    "ethereum", "01", "03", "04", "03"
)
X_test_eth, y_test_eth = make_time_series_dataset(
    "ethereum", "04", "05", "04", "07"
)
eth_ltsm = make_ts_model()
eth_ltsm.fit(X_ts_eth, y_ts_eth, epochs=500, batch_size=10)

# %% pycharm={"name": "#%%\n"}
evaluate_model("05/04/2022", "07/04/2022", eth_model, df_eth_test)

# %% [markdown] pycharm={"name": "#%% md\n"}
# Sentiment model significantly outperforms time series

# %% pycharm={"name": "#%%\n"}
X_ts_avax, y_ts_avax = make_time_series_dataset(
    "avalanche", "01", "03", "04", "03"
)
X_test_avax, y_test_avax = make_time_series_dataset(
    "avalanche", "04", "05", "04", "07"
)

avax_ltsm = make_ts_model()
avax_ltsm.fit(X_ts_avax, y_ts_avax, epochs=500, batch_size=10)

# %% pycharm={"name": "#%%\n"}
evaluate_model("05/04/2022", "07/04/2022", avax_model, df_avax_test)

# %% [markdown] pycharm={"name": "#%% md\n"}
# Sentiment is slightly more accurate but the price values are so small here its hard to say one way or another

# %% pycharm={"name": "#%%\n"}
X_ts_sol, y_ts_sol = make_time_series_dataset("solana", "01", "03", "04", "03")
X_test_sol, y_test_sol = make_time_series_dataset(
    "solana", "04", "05", "04", "07"
)

sol_ltsm = make_ts_model()
sol_ltsm.fit(X_ts_sol, y_ts_sol, epochs=500, batch_size=10)

# %% pycharm={"name": "#%%\n"}
evaluate_model("05/04/2022", "07/04/2022", sol_model, df_sol_test)

# %% [markdown] pycharm={"name": "#%% md\n"}
# Same as above

# %% pycharm={"name": "#%%\n"}
X_ts_doge, y_ts_doge = make_time_series_dataset("doge", "01", "03", "04", "03")
X_test_doge, y_test_doge = make_time_series_dataset(
    "doge", "04", "05", "04", "07"
)

doge_ltsm = make_ts_model()
doge_ltsm.fit(X_ts_doge, y_ts_doge, epochs=500, batch_size=10)

# %% pycharm={"name": "#%%\n"}
evaluate_model("05/04/2022", "07/04/2022", doge_model, df_doge_test)

# %% [markdown] pycharm={"name": "#%% md\n"}
# Slightly worse but again we're dealing with such small numbers here so idk

# %% [markdown]
# Tried making bigger model but not gonna use so ignore the rest of the code

# %% pycharm={"name": "#%%\n"}
df_tot = df_btc.copy()
df_tot = df_tot.append(df_sol)
df_tot = df_tot.append(df_avax)
df_tot = df_tot.append(df_eth)
df_tot = df_tot.append(df_doge)

X_tot = X_btc.copy()
X_tot = X_tot.append(X_sol)
X_tot = X_tot.append(X_avax)
X_tot = X_tot.append(X_eth)
X_tot = X_tot.append(X_doge)

y_tot = y_btc.copy()
y_tot = y_tot.append(y_sol)
y_tot = y_tot.append(y_avax)
y_tot = y_tot.append(y_eth)
y_tot = y_tot.append(y_doge)


# %% pycharm={"name": "#%%\n"}
price_df = X_tot["price"]
y_tot = (y_tot.sub(price_df, axis=0)).div(y_tot)
X_tot = X_tot[["authority", "vader_sentiment_compound"]]


# %% pycharm={"name": "#%%\n"}
tot_model = make_model(2)
tot_model.fit(X_tot, y_tot, batch_size=10, epochs=10)
