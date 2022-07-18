import datetime as dt
from eod import EodHistoricalData
import json
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
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


def get_closing_prices(folder= 'data_files', adj_close= False):
    """
    returns file with closing prices for selected securities
    """
    files = [file for file in os.listdir(folder) if not file.startswith('0')]

    closes = pd.DataFrame()

    for file in files:
        if adj_close:
            df = pd.DataFrame(pd.read_csv(f"{folder}/{file}",
                            index_col = 'date')['adjusted_close'])
            df.rename(columns={'adjusted_close': file[:-4]}, inplace=True)
        else:
            df = pd.DataFrame(pd.read_csv(f"{folder}/{file}",
                            index_col = 'date')['close'])
            df.rename(columns={'close': file[:-4]}, inplace=True)

        if closes.empty:
            closes = df
        else:
            closes = pd.concat([closes, df], axis = 1)
    closes.to_csv(f"{folder}/0-closes.csv")
    return closes                                                                        

def returns_from_closes(folder, filename):
    """
    returns instantaneous returns for selected securities
    """
    try:
        data = pd.read_csv(f"{folder}/{filename}", index_col=['date'])
        
    except Exception as e:
        print(f"There was a problem: {e}")            
    return np.log(data).diff().dropna()

def get_corr(data):
    """
    returns correl from securities
    """
    return data.corr()

def plot_closes(closes, relative=False):
    """
    plot absolute or relative closes for securities
    """
    if closes.endswith('.csv'):
        closes = pd.read_csv(closes, index_col=['date'])
    else:
        closes = pd.read_excel(closes, index_col=['date'])
    if relative:
        relative_change = closes / closes.iloc[0] - 1
        relative_change.plot()
        plt.axhline(0, c='r', ls='--')
        plt.grid(axis='y')
        plt.show()
    else:
        closes.plot()
        plt.grid(axis='y')
        plt.show()            

def get_return_data(*tickers, date=DEFAULT_DATE, adj_close=False, key):
    """
    saves closes and returns out to excel file named returns
    """
    client = EodHistoricalData(key)
    temp = pd.DataFrame()

    for ticker in tickers:
        try:
            if adj_close:
                temp[ticker] = pd.DataFrame(client.get_prices_eod(ticker,
                from_=date))['adjusted_close']
            else:
                temp[ticker] = pd.DataFrame(client.get_prices_eod(ticker,
                from_=date))['close']
        except Exception as e:
            print(f"{ticker} had a problem: {e}")
    data = temp
    data_instanteous = np.log(data).diff().dropna()
    data_pct = data.pct_change()

    with pd.ExcelWriter('returns.xlsx', datetime_format='yyyy-mm-dd') as writer:
        data.to_excel(writer, sheet_name='closes')
        data_instanteous.to_excel(writer, sheet_name='returns')
        data_pct.to_excel(writer, sheet_name='pct change')

    print(f"Data retrieved and saved to returns.xlsx in {os.getcwd()}")
    return data, data_instanteous, data_pct

def plot_performance(folder):
    """
    returns figure containing relative performance of all securities in folder
    """
    files = [file for file in os.listdir(folder) if not file.startswith('0')]
    fig, ax = plt.subplots(math.ceil(len(files)/ 4), 4, figsize=(16,16))
    count = 0
    for row in range(math.ceil(len(files)/ 4)):
        for column in range(4):
            try:
                data = pd.read_csv(f"{folder}/{files[count]}")['close']
                data = (data/data[0] -1) * 100
                ax[row,column].plot(data, label= files[count][:-4])
                ax[row,column].legend()
                ax[row,column].yaxis.set_major_formatter(mtick.PercentFormatter())
                ax[row,column].axhline(0, c='r', ls='--')
            except:
                pass
            count +=1
    plt.show()            

def get_earnings(key):
    """
    returns list of tickers for companies reporting in the next week
    """
    client =EodHistoricalData(key)
    eps = pd.DataFrame(client.get_calendar_earnings())
    symbols =[]

    for row in range(len(eps)):
        if eps.earnings.iloc[row]['code'].endswith('US'):
            symbols.append(eps.earnings[row]['code'][:-3])
    print(f"There are {len(symbols)} companies reporting this week")
    return symbols        


def get_dividends(key, exchange ='US', date= dt.date.today()):
    """
    returns securities with specific ex-date
    """
    client = EodHistoricalData(key)
    data = pd.DataFrame(client.get_bulk_markets(exchange= exchange,
                        date= date, type_='dividends'))
    return data                    


def screen_example(symbols, key):
    """
    Returns DataFrame with current price, 52-week high and ratio 
    of high to current price. Symbols is list-like
    """
    high = {}
    call = f"https://eodhistoricaldata.com/api/eod-bulk-last-day/US?api_token={key}&fmt=json"
    data = pd.DataFrame(requests.get(call).json())
    data.reset_index(drop=True)

    client = EodHistoricalData(key)
    for ticker in symbols:
        try:
            high[ticker] = client.get_fundamental_equity(f"{ticker}.US")['Technicals']['52WeekHigh']
            print(f"fetching {ticker}")
        except:
            print(f"{ticker} not available skipping")

    mask = data.code.isin(symbols)
    prices = data[['code', 'close']][mask]
    high = pd.Series(high, name='high')
    prices = prices.merge(high, right_on=high.index, left_on ='code')
    prices['ratio'] = prices['close'] / prices['high']
    return prices            
















def main():
    key = open('api_token.txt').read()
    # print(get_security_type(get_exchange_data(key)))
    # energy = get_sp(symbols=True, sector='Energy')
    # get_data("AAPL", "GOOG",key= key, path= 'mine')
    # get_closing_prices(folder='energy')
    # print(returns_from_closes('energy', '0-closes.csv'))
    # print(get_corr(returns_from_closes('energy','0-closes.csv')))
    # plot_closes(closes='mine/0-closes.csv',relative=True)
    # tickers = "AAPL AMZN GOOG NVDA".split()
    # returns = get_return_data(*tickers, key=key)
    # print(returns[0])
    # plot_performance('energy')
    # print(get_earnings(key))
    # print(get_dividends(key ))
    sp = get_sp()[:10]
    print(screen_example(sp,key))



if __name__ == '__main__':
    main()











