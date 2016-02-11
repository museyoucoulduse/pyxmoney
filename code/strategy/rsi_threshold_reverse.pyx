from code.strategy.dummy_strategy import DummyStrategy
from code.indicator.vwap import VWAP

import pandas as pd
import numpy as np


class RSI_Threshold_reverse(DummyStrategy):
    ''' RSI threshold '''
    def __init__(self, sl=500, tp=700, **kwargs):
        DummyStrategy.__init__(self, sl, tp)
        self.algo_name = 'RSI_Threshold_reverse'


    def check_data_for_trades(self, df1, sl, tp, **kwargs):
        # // checkEquity();
        self.trades.clear_trades()
        ind = VWAP(df1)
        df1['vwap'] = ind.caluculate()
        std = df1.std()
        sl = std.vwap/3*2
        tp = std.vwap/3*2 * 3
        print('In-strategy sl {} and tp {}'.format(sl, tp))

        window_length = 12

        def RSI(series, period):
            delta = series.diff().dropna()
            u = delta * 0
            d = u.copy()
            u[delta > 0] = delta[delta > 0]
            d[delta < 0] = -delta[delta < 0]
            u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
            u = u.drop(u.index[:(period-1)])
            d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
            d = d.drop(d.index[:(period-1)])
            rs = pd.stats.moments.ewma(u, com=period-1, adjust=False) / \
                pd.stats.moments.ewma(d, com=period-1, adjust=False)
            return 100 - 100 / (1 + rs)

        RSI1 = RSI(df1['closeBid'], window_length)


        lim = df1.index[14]
        # close = df1.vwap
        # # Get the difference in price from previous step
        # delta = close.diff()
        # # Get rid of the first row, which is NaN since it did not have a previous
        # # row to calculate the differences
        # # delta = delta[1:]

        # # Make the positive gains (up) and negative gains (down) Series
        # up, down = delta.copy(), delta.copy()
        # up[up < 0] = 0
        # down[down > 0] = 0

        # window_length = 12
        # # Calculate the EWMA
        # roll_up1 = pd.stats.moments.ewma(up, window_length)
        # roll_down1 = pd.stats.moments.ewma(down.abs(), window_length)

        # # Calculate the RSI based on EWMA
        # RS1 = roll_up1 / roll_down1
        # RSI1 = 100.0 - (100.0 / (1.0 + RS1))
        for i in df1.index:
            if i > lim:
                if RSI1[i] > 75 and RSI1[i-1] < 75:
                    self.trades.add_trade(i + df1.index[0], 'short', sl, tp)
                elif RSI1[i] < 25 and RSI1[i-1] > 25:
                    self.trades.add_trade(i + df1.index[0], 'long', sl, tp)
