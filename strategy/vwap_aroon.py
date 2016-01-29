from strategy.dummy_strategy import DummyStrategy
from indicator.vwap import VWAP

import pandas as pd

class VWAP_Aroon(DummyStrategy):
    ''' Aroon Oscillator on VWAP price '''
    def __init__(self, sl=500, tp=700, aroon_span=25, **kwargs):
        DummyStrategy.__init__(self, sl, tp)
        self.aroon_span = aroon_span
        self.algo_name = 'VWAP_Aroon'

    def desciption(self):
        print('This strategy responds better to market with VWAP, stoploss {} and takeprofit {}'
              .format(self.sl, self.tp))

    def check_data_for_trades(self, df1, sl, tp, aroon_span=None, **kwargs):
        # // checkEquity();
        self.trades.clear_trades()
        if aroon_span is None:
            aroon_span = self.aroon_span
        ind = VWAP(df1)
        df1['vwap'] = ind.caluculate()
        std = df1.std()
        sl = std.vwap
        tp = std.vwap * 3
        print('In-strategy sl {} and tp {}'.format(sl, tp))
        lim = df1.index[aroon_span]
        vwap = []
        for i, data in df1.iterrows():
            vwap.append(data.vwap)
            if i > lim:
                if df1.index[0] > 0:
                    i = i - df1.index[0]
                df_aroon = pd.DataFrame(vwap, columns=['vwap'])
                aroon_up = 100 * (aroon_span - (i - df_aroon[i-aroon_span:i-1].vwap.idxmax())) / aroon_span
                aroon_down = 100 * (aroon_span - (i - df_aroon[i-aroon_span:i-1].vwap.idxmin())) / aroon_span
                aroon_up2 = 100 * (aroon_span - (i-1 - df_aroon[i-aroon_span-1:i-2].vwap.idxmax())) / aroon_span
                aroon_down2 = 100 * (aroon_span - (i-1 - df_aroon[i-aroon_span-1:i-2].vwap.idxmin())) / aroon_span
                aroon = aroon_up - aroon_down
                aroon2 = aroon_up2 - aroon_down2

                def rising(series):
                    return (aroon2 < aroon)

                def falling(series):
                    return (aroon2 > aroon)

                if rising(aroon) and \
                (aroon < 0) and \
                (aroon2 <= -90):
                    self.trades.add_trade(i + df1.index[0], 'long', sl, tp)
                if falling(aroon) and \
                (aroon > 0) and \
                (aroon2 >= 90):
                    self.trades.add_trade(i + df1.index[0], 'short', sl, tp)
