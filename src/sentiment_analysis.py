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
# # Performing Sentiment Analysis via Textblob and VADER

# %%
import re
import string
from os.path import dirname, join, realpath

import nltk
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob


# %%
def is_interactive():
    """Check if the script is being run interactively."""
    import __main__ as main

    return not hasattr(main, "__file__")


if is_interactive():
    SCRIPT_DIR = dirname(realpath("__file__"))
else:
    SCRIPT_DIR = dirname(realpath(__file__))

DATA_DIR = join(SCRIPT_DIR, "data", "processed", "twitter")

# %% pycharm={"name": "#%%\n"}
data = pd.read_csv(join(DATA_DIR, "tweets_2022_03_05-2022_03_11.csv"))
data.head()

# %% [markdown]
# ## Clean Tweets

# %% pycharm={"name": "#%%\n"}
text_data = data[
    [
        "Unnamed: 0",
        "name",
        "verified",
        "created_at",
        "retweet_count",
        "favorite_count",
        "followers_count",
        "hashtags",
        "text",
    ]
]
text_data = text_data.rename(columns={"Unnamed: 0": "tweet_id"})
text_data.head()

# %% pycharm={"name": "#%%\n"}
punctuation = string.punctuation
punctuation = punctuation.replace("#", "")
punctuation = punctuation.replace("@", "")


def remove_punctuation(text):
    punctuationfree = "".join([i for i in text if i not in punctuation])
    return punctuationfree


# %% pycharm={"name": "#%%\n"}
def tokenization(text):
    tokens = re.split("W+", text)
    return tokens


# %% pycharm={"name": "#%%\n"}
nltk.download("stopwords")
stopwords = nltk.corpus.stopwords.words("english")


def remove_stopwords(text):
    output = [i for i in text if i not in stopwords]
    return output


# %% pycharm={"name": "#%%\n"}
nltk.download("wordnet")
wordnet_lemmatizer = WordNetLemmatizer()


def lemmatizer(text):
    lemm_text = [wordnet_lemmatizer.lemmatize(word) for word in text]
    return lemm_text


# %% pycharm={"name": "#%%\n"}
def clean_text(text):
    text["clean_text"] = text["text"].apply(lambda x: remove_punctuation(x))
    text["clean_text"] = text["clean_text"].apply(lambda x: x.lower())
    text["clean_text"] = text["clean_text"].apply(lambda x: tokenization(x))
    text["clean_text"] = text["clean_text"].apply(
        lambda x: remove_stopwords(x)
    )
    text["clean_text"] = text["clean_text"].apply(lambda x: lemmatizer(x))
    clean = text
    return clean


# %% pycharm={"name": "#%%\n"}
text_data = clean_text(text_data)
text_data.head()

# %% pycharm={"name": "#%%\n"}
text_data.info()


# %% [markdown]
# ## Sentiment Analysis

# %% pycharm={"name": "#%%\n"}
def textblob_polarity(text):
    return TextBlob(text).sentiment.polarity


# %% pycharm={"name": "#%%\n"}
text_data["textblob_sentiment"] = (
    text_data["clean_text"].astype("str").apply(textblob_polarity)
)


# %% pycharm={"name": "#%%\n"}
def textblob_sentiment_summary(text):
    sentiment = "Neutral"
    if text > 0:
        sentiment = "Positive"
    elif text < 0:
        sentiment = "Negative"
    return sentiment


# %% pycharm={"name": "#%%\n"}
text_data["textblob_summary"] = text_data["textblob_sentiment"].apply(
    lambda x: textblob_sentiment_summary(x)
)

# %% pycharm={"name": "#%%\n"}
text_data.head()

# %% pycharm={"name": "#%%\n"}
nltk.download("vader_lexicon")
sid = SentimentIntensityAnalyzer()

# %% pycharm={"name": "#%%\n"}
text_data["vader_sentiment_pos"] = (
    text_data["clean_text"].astype("str")
).apply(lambda x: sid.polarity_scores(x)["pos"])
text_data["vader_sentiment_neg"] = (
    text_data["clean_text"].astype("str")
).apply(lambda x: sid.polarity_scores(x)["neg"])
text_data["vader_sentiment_neu"] = (
    text_data["clean_text"].astype("str")
).apply(lambda x: sid.polarity_scores(x)["neu"])
text_data["vader_sentiment_compound"] = (
    text_data["clean_text"].astype("str")
).apply(lambda x: sid.polarity_scores(x)["compound"])


# %% pycharm={"name": "#%%\n"}
def vader_sentiment_summary(text):
    sentiment = "Neutral"
    if text >= 0.05:
        sentiment = "Positive"
    elif text <= -0.05:
        sentiment = "Negative"
    return sentiment


# %% pycharm={"name": "#%%\n"}
text_data["vader_summary"] = text_data["vader_sentiment_compound"].apply(
    lambda x: vader_sentiment_summary(x)
)

# %% pycharm={"name": "#%%\n"}
text_data.info()

# %% [markdown]
# ## Saving Analysis per Coin

# %% pycharm={"name": "#%%\n"}
bitcoin_sentiment = text_data[text_data["text"].str.contains("bitcoin|BTC")]
ethereum_sentiment = text_data[text_data["text"].str.contains("ethereum|ETH")]
doge_sentiment = text_data[text_data["text"].str.contains("dogecoin|DOGE")]
avalanche_sentiment = text_data[
    text_data["text"].str.contains("avalanche|AVAX")
]
solana_sentiment = text_data[text_data["text"].str.contains("solana|SOL")]
crypto_sentiment = text_data[
    text_data["text"].str.contains("crypto|cryptocurrency|coin")
]

# %% pycharm={"name": "#%%\n"}
bitcoin_sentiment.to_csv(join(DATA_DIR, "bitcoin_sentiment.csv"))
bitcoin_sentiment.head()

# %% pycharm={"name": "#%%\n"}
ethereum_sentiment.to_csv(join(DATA_DIR, "ethereum_sentiment.csv"))
ethereum_sentiment.head()

# %% pycharm={"name": "#%%\n"}
doge_sentiment.to_csv(join(DATA_DIR, "doge_sentiment.csv"))
doge_sentiment.head()

# %% pycharm={"name": "#%%\n"}
solana_sentiment.to_csv(join(DATA_DIR, "solana_sentiment.csv"))
solana_sentiment.head()

# %% pycharm={"name": "#%%\n"}
avalanche_sentiment.to_csv(join(DATA_DIR, "avalanche_sentiment.csv"))
avalanche_sentiment.head()

# %% pycharm={"name": "#%%\n"}
crypto_sentiment.to_csv(join(DATA_DIR, "crypto_sentiment.csv"))
crypto_sentiment.head()

# %% pycharm={"name": "#%%\n"}
len_doge = len(doge_sentiment)
len_btc = len(bitcoin_sentiment)
len_avax = len(avalanche_sentiment)
len_eth = len(ethereum_sentiment)
len_sol = len(solana_sentiment)

print(len(text_data) - len_doge - len_sol - len_eth - len_btc - len_avax)
print(
    len(text_data)
    - len_doge
    - len_sol
    - len_eth
    - len_btc
    - len_avax
    - len(crypto_sentiment)
)

# %% [markdown] pycharm={"name": "#%% md\n"}
# Not all the tweets pertain to the coins - there is clearly some error within the API as there are some tweets with no hashtags or mention of the specified criteria. Perhaps it pulled in some viral tweets that were important across all spaces despite not explicitly mentioning the keywords.
