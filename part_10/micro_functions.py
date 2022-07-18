from eod import EodHistoricalData
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import os
import pandas as pd
import seaborn as sb
sb.set_theme()

DEFAULT_DATE = dt.date.isoformat(dt.date.today() - dt.timedelta(396))


class Stock:
    def __init__(self, symbol, key, date =DEFAULT_DATE, folder=None):
        self.symbol = symbol
        self.key = key
        self.date = date
        self.folder = folder
        self.data = self.get_data()


    def get_data(self):
        available_data = [filename[:-4] 
        for filename in os.listdir(self.folder) if not filename.startswith('0')]
        if self.symbol in available_data:
            data = pd.read_csv(f"{self.folder}/{self.symbol}.csv", 
                                index_col='date').round(2)
        else:
            client = EodHistoricalData(self.key)
            data = pd.DataFrame(client.get_prices_eod(self.symbol,
                                from_=self.date)).round(2)
            data.index = pd.DatetimeIndex(data.date).date
            data.drop(columns=['date'], inplace = True)

        return data                                                







def main():
    KEY = open('api_token.txt').read()
    test = Stock(symbol='AAPL', key=KEY)
    print(test.data)

if __name__ == '__main__':
    main()    








