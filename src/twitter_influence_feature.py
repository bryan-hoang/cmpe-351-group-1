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
# # Creating features to measure a tweet's influence
#
# References:
# - https://medium.com/@tijesunimiolashore/mining-data-on-twitter-3c7969207e75
# - https://medium.com/@brianodhiambo530/twitter-mining-and-analysis-on-influential-twitter-users-and-africa-government-officials-a61fced65e38
# - https://towardsdatascience.com/twitter-data-mining-measuring-users-influence-ef76c9badfc0
#
# Results:
# - Popularity score = Retweets + Likes
# - Reach score = Followers - Following (N/A)
# - Relevance_score = Comments + Mentions (N/A)

# %%
from os.path import dirname, join, realpath

import pandas as pd


# %%
def is_interactive():
    """Check if the script is being run interactively."""
    import __main__ as main

    return not hasattr(main, "__file__")


if is_interactive():
    SCRIPT_DIR = dirname(realpath("__file__"))
else:
    SCRIPT_DIR = dirname(realpath(__file__))

DATA_DIR = join(dirname(SCRIPT_DIR), "data", "processed", "twitter")

# %%
tweet_data = pd.read_csv(join(DATA_DIR, "tweets_2022_03_05-2022_03_11.csv"))
# Drop 2 unnamed columns.
tweet_data.drop(columns=["Unnamed: 0", "Unnamed: 0.1"], inplace=True)
tweet_data.head()

# %%
tweet_data["popularity"] = (
    tweet_data["retweet_count"] + tweet_data["favorite_count"]
)
# Remove combined features.
tweet_data = tweet_data.drop(["retweet_count", "favorite_count"], axis=1)
tweet_data.to_csv(
    join(DATA_DIR, "tweets_2022_03_05-2022_03_11_popularity.csv"), index=False
)
tweet_data.head()

# %%
