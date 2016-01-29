#!/usr/bin/env python3

from strategy.vwap_aroon import VWAP_Aroon
from strategy.dummy_strategy import DummyStrategy
from src.profit import Profit
from src.colors import Colors
from src.instruments import Instruments
from src.granularity import Granularity
from src._helpers import _helpers

from pyoanda import Client, PRACTICE
import json
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import random
import os


class Backtester:
    ''' This class is ment to runt the strategy backtest and optimization '''
    def __init__(self, strategy=None, instrument=None, timeframe=None, end=None):
        self.client = Client(
            environment=PRACTICE,
            account_id='839834',
            access_token='d7873627d812178153033331c9b3c419-51738cf1315b4c36ef4ee628ca656a5d'
        )
        self.instruments = Instruments(self.client)
        self.instrument = self.instruments.instruments
        random.shuffle(self.instrument)
        self.ticker = instrument
        self.pips = self.instruments.pips
        self.strategy = strategy
        self.timeframe = Granularity.timeframes
        random.shuffle(self.timeframe)
        self.tf = timeframe
        self.save_plot = False
        if type(end) is not dt.datetime:
            self.end = dt.datetime(end).isoformat()
        else:
            self.end = end.isoformat()

    def connect(self):

        def _connecting(ticker, timeframe):
            df = self.get_history(ticker, timeframe)
            sl = _helpers._correct_pips(self.strategy.sl, ticker, self.instrument, self.pips)
            tp = _helpers._correct_pips(self.strategy.tp, ticker, self.instrument, self.pips)
            seconds = _helpers._getGranularitySeconds(tf)
            opt_end = dt.datetime.now() - dt.timedelta(seconds=seconds) * 5000
            print('From {} to {}'.format(opt_end, dt.datetime.now()))
            print('{} {} sl:{} tp:{}'.format(ticker, timeframe, sl, tp))
            self.backtest(df, sl, tp, ticker, timeframe, live=True)

        if self.ticker is None:
            for ins in self.instrument:
                if self.tf is None:
                    for tf in self.timeframe:
                        _connecting(ins, tf)
                else:
                    _connecting(ins, self.tf)
        else:
            _connecting(self.ticker, self.tf)

    def backtest(self, data, sl, tp, ticker, tf, live=False, **kwargs):

        self.strategy.check_data_for_trades(data, sl, tp)
        trdlst = self.strategy.trades.list_trades()
        profit = Profit(data, trdlst)
        total_pnl = profit.total_profit()
        if live:
            start = 'LIVE {}@{} total profit: '.format(ticker, tf)
        else:
            start = '{}@{} total profit: '.format(ticker, tf)
        if total_pnl > 0:
            print(start + Colors.OKGREEN + '{:.4f}'.format(total_pnl) +
                  Colors.ENDC + ' maximum drawdown: {:.2f} in {} trades'.format(
                  profit.max_drawdown(), profit.trades))
        else:
            print(start + Colors.FAIL + '{:.4f}'.format(total_pnl) +
                  Colors.ENDC + ' maximum drawdown: {:.2f} in {} trades'.format(
                  profit.max_drawdown(), profit.trades))

        # self.strategy.desciption()
        if self.save_plot:
            if not os.path.exists('./figures' + granularity) and not os.path.isdir('./figures' + granularity):
                os.makedirs('figures' + granularity)
            profitlst = profit.cumsum_profit()
            plt.plot(range(0, profit.trades), profitlst, linewidth=2.0)
            plt.title('{}'.format(ticker))
            plt.ylabel('{:.4f} pips in {} trades with max drawdown {:.2f}%'
                       .format(total_pnl, profit.trades, profit.max_drawdown()))
            seconds = _helpers._getGranularitySeconds(tf)
            opt_end = dt.timedelta(seconds=seconds) * 5000
            plt.xlabel('{}@{} {} trading for {} days with sl {:.4f} and tp {:.4f}'
                       .format(ticker, profit.actual_prices()[-1:].values[0], tf,
                       opt_end.days, trdlst[-1][2], trdlst[-1][3]))
            plt.savefig('figures/{}_{}@{}.png'.format(self.strategy.algo_name, ticker, tf),
                        dpi=None, facecolor='w', edgecolor='w',
                        orientation='portrait', papertype=None, format=None,
                        transparent=False, bbox_inches=None, pad_inches=0.1,
                        frameon=None)
            plt.close()

    def optimize(self, ticker=None, tf=None, min_sl=0, min_tp=0, max_sl=2000, max_tp=6000, steps=20):
        ''' Optimization method running bruteforce '''
        if ticker is None:
            ticker = self.instrument

        if tf is None:
            tf = 'H1'

        seconds = _helpers._getGranularitySeconds(tf)
        opt_end = dt.datetime.now() - dt.timedelta(seconds=seconds) * 5000
        print('From {} to {}'.format(opt_end - dt.timedelta(seconds=seconds) * 5000,
              dt.datetime.now()))



        def opt_loop(ticker, tf, min_sl, min_tp, max_sl, max_tp, steps):
            try:
                data = self.get_history(ticker, tf)
                data2 = self.get_history(ticker, tf, end=opt_end.isoformat())
            except:
                data = self.get_history(ticker, tf)
                data2 = data[:int(len(data.index)/2)].copy()
                data = data[int(len(data.index)/2)-1:].copy()
            steps_sl = int(max_sl / steps)
            steps_tp = int(max_tp / steps)
            for sl in range(min_sl, max_sl, steps_sl):
                sl = _helpers._correct_pips(sl, ticker, self.instrument, self.pips)
                for tp in range(min_tp, max_tp, steps_tp):
                    tp = _helpers._correct_pips(tp, ticker, self.instrument, self.pips)
                    print('OPTIMIZATION {} {} sl:{} tp:{}'.format(ticker, tf, sl, tp))
                    self.backtest(data2, sl, tp, ticker, tf)
                    print('LIVE {} {} sl:{} tp:{}'.format(ticker, tf, sl, tp))
                    self.backtest(data, sl, tp, ticker, tf, live=True)

        if ticker is not str:
            for asset in ticker:
                opt_loop(asset, tf, min_sl, min_tp, max_sl, max_tp, steps)
        else:
            opt_loop(ticker, tf, min_sl, min_tp, max_sl, max_tp, steps)

    def get_history(self, ticker, timeframe, count='5000', end=dt.datetime.now().isoformat()):
        data = self.client.get_instrument_history(instrument=ticker,
            granularity=timeframe, count='5000', end=end)
        df = pd.read_json(json.dumps(data['candles']))
        return df
