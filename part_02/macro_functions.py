import json
import pandas as pd
import requests


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


def main():
    key = open('api_token.txt').read()
    #print(get_security_type(get_exchange_data(key)))
    print(get_sp(symbols=False, sector='Energy'))

if __name__ == '__main__':
    main()











