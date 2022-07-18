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
            self.calc_vol(data)
        return data

    def calc_vol(self, df):
        df['returns'] = np.log(df.close).diff().round(4)
        df['volatility'] = df.returns.rolling(21).std().round(4)
        df['change'] = df['close'].diff()
        df['hi_low_spread'] = ((df['high'] -df['low']) / df['open']).round(2)
        df['exp_change'] = (df.volatility * df.close.shift(1)).round(2)
        df['magnitude'] = (df.change / df.exp_change).round(2)
        df['abs_magnitude'] = np.abs(df.magnitude)
        df.dropna(inplace= True)

    def plot_return_dist(self):
        start = self.data.index[0]
        end  = self.data.index[-1]
        plt.hist(self.data['returns'], bins=20, edgecolor='w')
        plt.suptitle(f"Distribution of returns for {self.symbol}", fontsize=14)
        plt.title(f"From {start} to {end}", fontsize=12)
        plt.show()


    def plot_volatility(self):
        start = self.data.index[0]
        end  = self.data.index[-1]
        plt.scatter(self.data['returns'], self.data['abs_magnitude'])
        plt.axhline(0, c='r', ls='--')
        plt.axvline(0, c='r', ls='--')
        plt.suptitle(f"Volatility of returns for {self.symbol}", fontsize=14)
        plt.title(f"From {start} to {end}", fontsize=12)
        plt.show()

    def plot_performance(self):
        start = self.data.index[0]
        end  = self.data.index[-1]
        plt.plot((self.data.close / self.data.close[0] - 1) * 100)
        plt.axhline(0, c='r', ls='--')
        plt.suptitle(f"Volatility of returns for {self.symbol}", fontsize=14)
        plt.title(f"From {start} to {end}", fontsize=12)
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())
        plt.show()    








def main():
    KEY = open('api_token.txt').read()
    test = Stock(symbol='AAPL', key=KEY)
    #print(test.data)
    test.plot_performance()

if __name__ == '__main__':
    main()    








