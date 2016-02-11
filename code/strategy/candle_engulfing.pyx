from code.strategy.dummy_strategy import DummyStrategy
from code.indicator.vwap import VWAP

import pandas as pd
import numpy as np


class Candle_Engulfing(DummyStrategy):
    ''' Candle pattern - engulfing '''
    def __init__(self, sl=500, tp=700, bar1size=40, **kwargs):
        DummyStrategy.__init__(self, sl, tp)
        self.bar1size = bar1size
        self.algo_name = 'Candle_Engulfing'


    def check_data_for_trades(self, df1, sl, tp, bar1size=None, **kwargs):
        # // checkEquity();
        self.trades.clear_trades()
        if bar1size is None:
            bar1size = self.bar1size
        ind = VWAP(df1)
        df1['vwap'] = ind.caluculate()
        std = df1.std()
        sl = std.vwap/3*2
        tp = std.vwap/3*2 * 3
        bar1size = std.vwap/4*3
        print('In-strategy sl {} and tp {}'.format(sl, tp))
        interval = 2.5
        lim = df1.index[2]
        buy_stop = [0, 0]
        sell_stop = [0, 0]
        for i in df1.index:
            if i > lim:

                if buy_stop[0] != 0:

                    if df1['highAsk'][buy_stop[0]:i].max() > buy_stop[1]:
                        self.trades.add_trade(i + df1.index[0], 'long', sl, tp)
                        buy_stop = [0, 0]
                if sell_stop[0] != 0:
                    if df1['lowBid'][sell_stop[0]:i].min() < sell_stop[1]:
                        self.trades.add_trade(i + df1.index[0], 'short', sl, tp)
                        sell_stop = [0, 0]
                try:
                    open1 = df1['openMid'][i:].values[0]
                    open2 = df1['openMid'][i-1:i].values[0]
                    close1 = df1['closeMid'][i:].values[0]
                    close2 = df1['closeMid'][i-1:i].values[0]
                    low1 = df1['lowMid'][i:].values[0]
                    low2 = df1['lowMid'][i-1:i].values[0]
                    high1 = df1['highMid'][i:].values[0]
                    high2 = df1['highMid'][i-1:i].values[0]
                    _bar1size = (high1-low1)
                except:
                    open1 = df1['openBid'][i:].values[0]
                    open2 = df1['openBid'][i-1:i].values[0]
                    close1 = df1['closeBid'][i:].values[0]
                    close2 = df1['closeBid'][i-1:i].values[0]
                    low1 = df1['lowBid'][i:].values[0]
                    low2 = df1['lowBid'][i-1:i].values[0]
                    high1 = df1['highBid'][i:].values[0]
                    high2 = df1['highBid'][i-1:i].values[0]
                    _bar1size = (high1-low1)

                if _bar1size > bar1size \
                and low1 <= low2 \
                and high1 >= high2 \
                and close1 <= open2 \
                and open1 >= close1 \
                and open2 <= close2 \
                and sell_stop[0] == 0 \
                or sell_stop[0] - i > 5:
                    sell_stop[0] = i
                    sell_stop[1] = low1

                if _bar1size > bar1size \
                and low1 <= low2 \
                and high1 >= high2 \
                and close1 >= open2 \
                and open1 <= close1 \
                and open2 >= close2 \
                and buy_stop[0] == 0 \
                or buy_stop[0] - i > 5:
                    buy_stop[0] = i
                    buy_stop[1] = high1
