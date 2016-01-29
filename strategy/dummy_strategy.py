from src.trades import Trades

import pandas as pd


class DummyStrategy:
    ''' Implementing basic Strategy object '''
    def __init__(self, mystoploss=25, mytakeprofit=65, **kwargs):
        self.sl = mystoploss
        self.tp = mytakeprofit
        self.trades = Trades()
        self.algo_name = 'DummyStrategy'

    def desciption(self):
        print('This is dummy strtegy with stoploss {} and takeprofit {}'
              .format(self.sl, self.tp))

    def check_data_for_trades(self, df, sl, tp):
        lim = df.index[0]
        for i, data in df.iterrows():
            if i > lim:
                if df.index[0] > 0:
                    i = i - df.index[0]

                def rising(series):
                    return series[-2:-1].closeBid.item() < series[-1:].closeBid.item()

                def falling(series):
                    return series[-2:-1].closeBid.item() > series[-1:].closeBid.item()

                if rising(df):
                    self.trades.add_trade(i + df.index[0], 'long', sl, tp)
                if falling(df):
                    self.trades.add_trade(i + df.index[0], 'short', sl, tp)
