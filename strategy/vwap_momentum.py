from strategy.dummy_strategy import DummyStrategy
from indicator.vwap import VWAP

import pandas as pd
import numpy as np


class VWAP_Momentum(DummyStrategy):
    ''' Aroon Oscillator on VWAP price '''
    def __init__(self, sl=500, tp=700, momentum_span=25, **kwargs):
        DummyStrategy.__init__(self, sl, tp)
        self.momentum_span = momentum_span
        self.algo_name = 'VWAP_Momentum'

    def desciption(self):
        print('This strategy responds better to market with VWAP, stoploss {} and takeprofit {}'
              .format(self.sl, self.tp))


    def check_data_for_trades(self, df1, sl, tp, momentum_span=None, **kwargs):
        # // checkEquity();
        self.trades.clear_trades()
        if momentum_span is None:
            momentum_span = self.momentum_span
        ind = VWAP(df1)
        df1['vwap'] = ind.caluculate()
        std = df1.std()
        sl = std.vwap
        tp = std.vwap * 3
        print('In-strategy sl {} and tp {}'.format(sl, tp))
        lim = df1.index[momentum_span]
        for i in df1.index:
            if i > lim:
                mom = pd.ewma(df1.vwap, span=np.floor(momentum_span/2)) - pd.ewma(df1.vwap,span=momentum_span)
                mom2 = pd.ewma(df1.vwap, span=np.floor(np.sqrt(momentum_span)))

                def rising(series, y):
                    return (series[y-1].item() < series[y].item())

                def falling(series, y):
                    return (series[y-1].item() > series[y].item())

                if rising(mom2, i) and \
                (mom[i] > 0) and \
                (mom[i-1] <= 0):
                    self.trades.add_trade(i + df1.index[0], 'long', sl, tp)
                    # crossover.append([i, 'long', mystoploss, mytakeprofit])
                if falling(mom2, i) and \
                (mom[i] < 0) and \
                (mom[i-1] >= 0):
                    self.trades.add_trade(i + df1.index[0], 'short', sl, tp)
                    # crossover.append([i, 'short' ,mystoploss, mytakeprofit])
