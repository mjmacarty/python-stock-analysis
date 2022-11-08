import datetime as dt
from eod import EodHistoricalData
import json
import os
import pandas as pd
import requests

DEFAULT_DATE = dt.date.today() - dt.timedelta(396)
TODAY =dt.date.today()



def get_exchange_data(key, exchange='NYSE'):
    """
    returns metadata for a specific exchange
    available: US, NASDAQ, OTCBB, PINK, BATS
    """
    endpoint = f"https://eodhistoricaldata.com/api/exchange-symbol-list/"
    endpoint += f"{exchange}?api_token={key}&fmt=json"
    print("Downloading data")
    call =requests.get(endpoint).text
    exchange_data = pd.DataFrame(json.loads(call))
    print("Completed")
    return exchange_data


def get_security_type(exchange_data, type= "Common Stock"):
    """
    Returns a list of filtered security types
    Types available: Common Stock, ETF, Fund, Preferred Stock
    """
    symbols = exchange_data[exchange_data.Type == type]
    return symbols.Code.to_list()

def get_sp(symbols =True, sector= False):
    """
    returns S&P 500 metadata
    Sectors: Communication Services, Consumer Discretionary, Consumer Staples,
    Energy, Financials, Health Care, Industrials, Information Technology,
    Materials, Real Estate, Utilities
    """
    sp = pd.read_csv('sp500.csv')
    if sector:
        sp = sp[sp.Sector == sector]
    if symbols:
        return sp['Symbol']
    else:
        return sp 


def get_data(*tickers, key, path='data_files', date=DEFAULT_DATE):
    """
    downloads and stores as csv price data for selected securities
    """
    if not os.path.exists(f"{os.getcwd()}/{path}"):
        os.mkdir(path)
    downloaded = 0
    skipped = 0
    tickers_skipped = []

    client = EodHistoricalData(key)
    for ticker in tickers:
        try:
            print(f"Downloading {ticker}")
            df = pd.DataFrame(client.get_prices_eod(ticker, from_=date))
            df.index = pd.DatetimeIndex(df.date)
            df.drop(columns=['date'], inplace=True)
            df.to_csv(f"{path}/{ticker}.csv")
            downloaded += 1
        except:
            print(f"{ticker} not found, skipping...")
            skipped += 1
            tickers_skipped.append(ticker)
    print("Download completed")
    print(f"Data download for {downloaded} securities")
    print(f"{skipped} tickers skipped")
    if tickers_skipped:
        print(" Tickers skipped ".center(30, "="))
        for ticker in tickers_skipped:
            print(ticker)                         




def main():
    key = open('api_token.txt').read()
    #print(get_security_type(get_exchange_data(key)))
    energy = get_sp(symbols=True, sector='Energy')
    get_data("AAPL", "GOOG",key= key, path= 'mine')

if __name__ == '__main__':
    main()











