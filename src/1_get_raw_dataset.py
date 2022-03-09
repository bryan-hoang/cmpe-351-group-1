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
from pandas import DataFrame, DatetimeIndex
from pandas import concat as concat_df
from pandas import date_range

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

# "../data"
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
CRYPTOCURRENCIES = ["BTC", "ETH", "DOGE", "SOL", "AVAX"]
# The last 7 days is the limit of the minute data from crypto compare.
NUM_DAYS = 7
DATE_RANGE = date_range(end=datetime.today(), periods=NUM_DAYS)


def get_and_save_crypto_dataset(
    cryptocurrencies: list[str], time_period: DatetimeIndex, save_folder: str
):
    """Get cryptocurrency data and save it to a csv file."""
    for cryptocurrency in cryptocurrencies:
        price_dataset = []
        for date in time_period:
            price_dataset += get_historical_price_minute(
                cryptocurrency, "USD", limit=1440, toTs=date
            )

        # Saving the raw price data to a csv file.
        price_data_frame = DataFrame(price_dataset)
        price_data_frame.to_csv(
            join(
                save_folder,
                "raw",
                "crypto",
                f"{cryptocurrency.lower()}"
                f"_{time_period[0].strftime('%Y_%m_%d')}"
                f"-{time_period[-1].strftime('%Y_%m_%d')}_minute.csv",
            )
        )


get_and_save_crypto_dataset(CRYPTOCURRENCIES, DATE_RANGE, DATA_DIR)

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


date_today = datetime.today().strftime("%Y-%m-%d")


def make_df(hashtag_list, until_date=date_today, result_type="popular"):
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
    join(
        DATA_DIR,
        "raw",
        "twitter",
        f"tweets_{date_today}.csv".replace("-", "_"),
    )
)

df.head()
