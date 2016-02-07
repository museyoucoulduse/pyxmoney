#!/usr/bin/env python3

from code.strategy.vwap_aroon import VWAP_Aroon
from code.strategy.dummy_strategy import DummyStrategy
from code.src.colors import Colors
from code.src.profit import Profit
from code.src.instruments import Instruments
from code.src.granularity import Granularity
from code.src._helpers import _helpers

from pyoanda import Client, PRACTICE, exceptions
import json
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import random
import os
from pymongo import MongoClient


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
        self.save_mongo = False
        self.mongo_connection = ''
        self.cur_mongo_obj = {}
        self.mongo_candles = None
        self.download = True

    def connect(self):

        def _connecting(ticker, timeframe):
            if False: #self.download is not True
                client = MongoClient(self.mongo_connection)
                db = client.oanda
                df = pd.read_json(json.dumps(db.oandaCandles.find_one({'ticker': ticker, 'tf': timeframe})['candles']))
                print('Loaded cached data')
            else:
                try:
                    print('Downloading data')
                    df = self.get_history(ticker, timeframe)
                except exceptions.BadRequest as e:
                    print("Houston, we've got a problem: ", e)
                    return None
                print('Ready')
                self.mongo_candles = df #
            sl = _helpers._correct_pips(self.strategy.sl, ticker, self.instrument, self.pips)
            tp = _helpers._correct_pips(self.strategy.tp, ticker, self.instrument, self.pips)
            seconds = _helpers._getGranularitySeconds(timeframe)
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
            if self.tf is None:
                for tf in self.timeframe:
                    _connecting(self.ticker, tf)
            else:
                _connecting(self.ticker, self.tf)

    def backtest(self, data, sl, tp, ticker, tf, live=False, **kwargs):
        if self.strategy.algo_name is 'VWAP_EWMA':
            self.strategy.check_data_for_trades(data, sl, tp, self.strategy.small, self.strategy.big)
        else:
            self.strategy.check_data_for_trades(data, sl, tp)
        trdlst = self.strategy.trades.list_trades()
        profit = Profit(data, trdlst)
        mongo_list_of_trades = trdlst #
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
        mongo_ticker = ticker #
        mongo_tf = tf #
        mongo_num_trades = profit.trades #
        if mongo_num_trades is 0:
            print('No trades... Skipping...')
            return None
        mongo_max_drawdown = profit.max_drawdown() #
        mongo_total_pnl = total_pnl #
        
        if self.save_plot:
            if not os.path.exists('./figures') and not os.path.isdir('./figures'):
                os.makedirs('figures')
            profit_cumsum = profit.cumsum_profit()
            plt.plot(range(0, profit.trades), profit_cumsum, linewidth=2.0)
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
        if self.save_mongo:
            # closer to zero is better
            mongo_last_price = profit.actual_prices()[-1:].values[0] #
            mongo_benchmark = (((-(mongo_max_drawdown) * mongo_num_trades) / mongo_total_pnl) *  mongo_total_pnl) * (mongo_last_price / 50) # 50 = margin
            mongo_profit_list = profit.profit_list() #
            mongo_profit_cumsum = profit.cumsum_profit().to_json()
            seconds = _helpers._getGranularitySeconds(tf)
            mongo_from = (dt.datetime.now() - (dt.timedelta(seconds=seconds) * self.mongo_candles.closeBid.count())).strftime('%Y%m%d%H%M%S') #
            mongo_to = dt.datetime.now().strftime('%Y%m%d%H%M%S') #
            
            cum_sl = []
            cum_tp = []
            for trd in trdlst:
                cum_sl.append(trd[2])
                cum_tp.append(trd[3])
                trd[0] = str(trd[0])
            mongo_mean_sl = pd.DataFrame(cum_sl).mean()[-1:].values[0] #                
            mongo_mean_tp = pd.DataFrame(cum_tp).mean()[-1:].values[0] #
            mongo_algo = self.strategy.algo_name #
            mongo_myid = mongo_ticker + '_' + mongo_tf + '_' + mongo_algo
            client = MongoClient(self.mongo_connection)
            print('Connecting to {}'.format(self.mongo_connection))
            db = client.oanda
            result = db.oandaTest.find_one({'myid': mongo_myid})
            if result is not None:
                db.oandaTest.update({
                    'myid': result['myid']
                    },
                    {
                        '$set': {
                            'mean_sl': mongo_mean_sl,
                            'mean_tp': mongo_mean_tp,
                            'last_price': mongo_last_price,
                            'from': mongo_from,
                            'to': mongo_to,
                            'max_drawdown': min(result['max_drawdown'], mongo_max_drawdown),
                            'trade_list': mongo_list_of_trades,
                            'profit_list': mongo_profit_list,
                            'profit_cumsum': mongo_profit_cumsum,
                            'total_pnl': mongo_total_pnl,
                            'num_trades': mongo_num_trades,
                            'benchmark': mongo_benchmark
                        }
                    })
            else:
                db.oandaTest.insert_one({
                    'myid': mongo_myid,
                    'ticker': mongo_ticker,
                    'tf': mongo_tf,
                    'algo': mongo_algo,
                    'from': mongo_from,
                    'mean_sl': mongo_mean_sl,
                    'mean_tp': mongo_mean_tp,
                    'last_price': mongo_last_price,
                    'to': mongo_to,
                    'max_drawdown': mongo_max_drawdown,
                    'total_pnl': mongo_total_pnl,
                    'num_trades': mongo_num_trades,
                    'trade_list': mongo_list_of_trades,
                    'profit_list': mongo_profit_list,
                    'profit_cumsum': mongo_profit_cumsum,
                    'benchmark': mongo_benchmark
                })
            if True: #self.download is True
                res_candles = db.oandaCandles.find_one({'ticker': mongo_ticker, 'tf': mongo_tf})
                if res_candles is not None:
                    db.oandaCandles.update({
                        'ticker': res_candles['ticker'],
                        'tf': res_candles['tf'],
                    },
                    {
                        "$set": {'candles': self.mongo_candles.to_json()} 
                    })
                else:
                    db.oandaCandles.insert_one({
                        'ticker': mongo_ticker,
                        'tf': mongo_tf,
                        'candles': self.mongo_candles.to_json()
                    })
            print('Benchmark: {}'.format(mongo_benchmark))
            print('Saved data successfully')
            client.close()
            print('Disconnected from database')
            

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
