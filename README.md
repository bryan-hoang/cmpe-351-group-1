# Predicting Value and Ranking Social Volatility of Cryptocurrency via Twitter

> The Dream Team's... dream!

A project for an undergraduate Advanced Data Analytics course that aims to analyze the relationship between tweets and cryptocurrencies.

## Developing

### Built With

- [The CryptoCompare API](https://min-api.cryptocompare.com/)
- [cryptocompare](https://github.com/lagerfeuer/cryptocompare#readme)
- [Tywthon](https://github.com/ryanmcgrath/twython#readme)

### Prerequisites

- [Python 3.10](https://www.python.org/downloads/)
- [Pipenv](https://github.com/pypa/pipenv#readme)

### Setting up Development Environment

```shell
git clone https://github.com/bryan-hoang/cmpe-351-group-1.git
cd cmpe-351-group-1/
pipenv install --dev
```

`pipenv install --dev` creates a virtual environment and installs all dependencies related to the project and for development. To activate the virtual environment, run `pipenv shell`.

## Configuration

For security, the code retrieves the secrets of API keys needed for building the dataset from environment variables. For convenience, the project uses `.env` files to store these secrets.

You will need to create a `.env` file at the root of the project and set the `CRYPTOCOMPARE_API_KEY`, `TWITTER_APP_KEY`, and `TWITTER_APP_SECRET` environment variables if you want to run [src/1_get_raw_dataset.ipynb](src/1_get_raw_dataset.ipynb). e.g.,

```txt
# .env
CRYPTOCOMPARE_API_KEY='YOUR_CRYPTOCOMPARE_API_KEY'
TWITTER_APP_KEY='YOUR_TWITTER_APP_KEY'
TWITTER_APP_SECRET='YOUR_TWITTER_APP_SECRET'
```

## Style guide

Python code should ideally follow the [Black](https://github.com/psf/black#the-black-code-style) style for consistency.

Since it's difficult to use auto formatting tools on `.ipynb` files, one can use [jupytext](https://github.com/mwouts/jupytext#readme) to convert `.ipynb` files into `.py` files to format them using `black`, and then convert them back by syncing the two files based on when they were lasted modified. e.g.,

```sh
# Sync the paired python file with changes from notebook.
jupytext --sync src/1_get_raw_dataset.ipynb
# Format the file. Can run the formatter through your editor/IDE.
black src/1_get_raw_dataset.py
# Sync the formatting changes in the script back to the paired notebook.
jupytext --sync src/1_get_raw_dataset.ipynb
```
