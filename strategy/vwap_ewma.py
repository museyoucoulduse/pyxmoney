from strategy.dummy_strategy import DummyStrategy
from indicator.vwap import VWAP

import pandas as pd
import numpy as np


class VWAP_Momentum(DummyStrategy):
    ''' Aroon Oscillator on VWAP price '''
    def __init__(self, sl=500, tp=700, small=30, big=60, **kwargs):
        DummyStrategy.__init__(self, sl, tp)
        self.small = small
        self.big = big
        self.algo_name = 'VWAP_EWMA'

    def desciption(self):
        print('This strategy responds better to market with VWAP, stoploss {} and takeprofit {}'
              .format(self.sl, self.tp))

    def check_data_for_trades(df1, small, big, sl, tp, **kwargs):
        self.trades.clear_trades()
        ind = VWAP(df1)
        df1['vwap'] = ind.caluculate()
        if small is None:
            small = self.small
        if big is None:
            big = self.big
        df1['small'] = pd.ewma(df1.vwap, span=small)
        df1['big'] = pd.ewma(df1.vwap, span=big)
        bool_table = df1['small'] > df1['big']
        bool_table2 = df1['small'] < df1['big']
        truth = bool_table | bool_table2
        df1['long'] = bool_table
        df1['short'] = bool_table2
        # // checkEquity();
        std = df1.std()
        sl = std.vwap
        tp = std.vwap * 3
        print('In-strategy sl {} and tp {}'.format(sl, tp))
        lim = df1.index[max(big, small)]
        long_ma = []
        short_ma = []
        for i, data in df1.iterrows():
            long_ma.append(data.long)
            short_ma.append(data.short)
            if small >= big:
                lim = small-1
            else:
                lim = big-1
                if i > df1.index[lim]:
                    if df1.index[0] > 0:
                        i = i - df1.index[0]
                    # val = long_ma[i]
                    # if val == True and long_ma[i - 1] == False:
                    #     self.trades.add_trade(i + df1.index[0], 'long', sl, tp)
                    # elif val == False and long_ma[i - 1] == True:
                    #     self.trades.add_trade(i + df1.index[0], 'short', sl, tp)
                    val = short_ma[i]
                    if val == True and short_ma[i - 1] == False:
                        self.trades.add_trade(i + df1.index[0], 'short', sl, tp)
                    elif val == False and short_ma[i - 1] == True:
                        self.trades.add_trade(i + df1.index[0], 'long', sl, tp)
