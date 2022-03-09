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
from pandas import concat as concat_df

# Twython API.
from twython import Twython


# %%
def is_interactive():
    """Check if the script is being run interactively."""
    import __main__ as main

    return not hasattr(main, "__file__")


if is_interactive():
    SCRIPT_DIR = dirname(realpath("__file__"))
else:
    SCRIPT_DIR = dirname(realpath(__file__))

DATA_DIR = join(dirname(SCRIPT_DIR), "data")

# %% [markdown]
# ## Initializing APIs.
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

twitter = Twython(TWITTER_APP_KEY, TWITTER_APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter = Twython(
    TWITTER_APP_KEY, TWITTER_APP_SECRET, access_token=ACCESS_TOKEN
)

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
twitter.search(count=1, q="cryptocurrency")

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

# %% [markdown]
# ## Getting Twitter data

# %%
tweet_data: dict = {
    "text": [],  # statuses
    "retweet_count": [],
    "favorite_count": [],
    "followers_count": [],
    "verified": [],
    "listed_count": [],
    "created_at": [],
    "hashtags": [],
    "name": [],
}

HASHTAG_LIST = [
    "#cryptocurrency",
    "#crypto",
    "#dogecoin",
    "#DOGE",
    "#bitcoin",
    "#BTC",
    "#ethereum",
    "#ENS",
    "#avalanche",
    "#AVAX",
    "#solana",
    "#SOL",
]


def read_tweets(search_results):
    """Read tweets from the search results into a data frame."""
    for i in range(len(search_results["statuses"])):
        for j, _ in tweet_data.items():
            if (
                (j == "text")
                or (j == "retweet_count")
                or (j == "favorite_count")
            ):
                tweet_data[j].append(search_results["statuses"][i][j])
            elif j == "hashtags":
                tweet_data[j].append(
                    search_results["statuses"][i]["entities"][j]
                )
            else:
                tweet_data[j].append(search_results["statuses"][i]["user"][j])

    return DataFrame(tweet_data)


date = datetime.today().strftime("%Y-%m-%d")


def make_df(hashtag_list, until_date=date, result_type="popular"):
    """Make a dataframe of tweets containing the specified hashtags."""
    count = 0
    tweets_dataframe = DataFrame()
    for i in hashtag_list:
        search_results = twitter.search(
            count=100, q=i, until=until_date, result_type=result_type
        )
        tweets_dataframe = concat_df(
            [tweets_dataframe, read_tweets(search_results)]
        )
        count = count + 1

    return tweets_dataframe


df = make_df(HASHTAG_LIST)

df.to_csv(
    join(DATA_DIR, "raw", "twitter", f"tweets_{date}.csv".replace("-", "_"))
)

df.head()
