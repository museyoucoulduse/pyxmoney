#!/usr/bin/env python3

from code.strategy.vwap_ewma import VWAP_EWMA
from code.strategy.vwap_momentum import VWAP_Momentum
from code.strategy.vwap_aroon import VWAP_Aroon
from code.src.backtester import Backtester

import datetime as dt
import argparse

if __name__ == '__main__':

    __author__ = 'neosb'

    parser = argparse.ArgumentParser(
        description='This is a backtesting platform using Oanda data from {}'
                    .format(__author__),
        prog='PyMoney')
    parser.add_argument(
        '-s', '--strategy', choices=['vwap_aroon', 'vwap_ewma', 'vwap_momentum'],
        help='choose one of the strategies')
    parser.add_argument(
        '-vwap_aroon', '--strategy_vwap_aroon',
        help='explicitly choose a VWAP_Aroon strategy',
        required=False, action='store_true')
    parser.add_argument(
        '-vwap_momentum', '--strategy_vwap_momentum',
        help='explicitly choose a VWAP_Momentum strategy',
        required=False, action='store_true')
    parser.add_argument(
        '-vwap_ewma', '--strategy_vwap_ewma',
        help='explicitly choose a VWAP_EWMA strategy',
        required=False, action='store_true')
    parser.add_argument(
        '-vwap_aroon_params', '--strategy_vwap_aroon_params',
        default=[500, 700, 25], metavar='VWAP_AROON_PARAMS',
        help='give parameters to VWAP_Aroon strategy: sl, tp and span',
        type=int, required=False)
    parser.add_argument(
        '-vwap_momentum_params', '--strategy_vwap_momentum_params',
        default=[500, 700, 40], metavar='VWAP_MOMENTUM_PARAMS',
        help='give parameters to VWAP_Momentum strategy: sl, tp and span',
        type=int, required=False)
    parser.add_argument(
        '-vwap_ewma_params', '--strategy_vwap_ewma_params',
        default=[500, 700, 25, 60], metavar='VWAP_EWMA_PARAMS',
        help='give parameters to VWAP_EWMA strategy: sl, tp, short ma and long ma',
        type=int, required=False)
    parser.add_argument(
        '-i', '--instrument', metavar='TICKER',
        help='instrument you want to test or leave to test on everything',
        required=False)
    parser.add_argument(
        '-tf', '--timeframe',
        help='set timeframe or leava blank to run test on every kind of granularity',
        required=False)
    parser.add_argument(
        '-e', '--end_date',
        help='set the end date of backtest and optimization',
        default=dt.datetime.now(),
        required=False, type=dt.datetime)
    parser.add_argument(
        '-op1', '--optimization_params1', metavar='OPT_PARAMS1',
        help='set ticker and timeframe for optimization, defualts to all assets at H1.',
        default=[None, None], required=False)
    parser.add_argument(
        '-op2', '--optimization_params2', metavar='OPT_PARAMS2',
        help='set min_sl, min_tp, max_sl, max_tp and steps for optimization.',
        default=[0, 0, 600, 900, 5], type=int, required=False)
    parser.add_argument(
        '-run_opt', '--run_optimization',
        help='set to True if you want to run optimization (currently supported: brutforce)',
        action='store_true', required=False)
    parser.add_argument(
        '-plt', '--save_plot',
        help='save realized profit and loss curve on plot' +
        'If you want to run multiple backtests or optimization you should not run this.',
        action='store_true', required=False
    )
    parser.add_argument(
        '-mongo', '--save_mongo',
        help='save realized profit and loss to MongoDB' +
        'If you want to run multiple backtests you should run this.',
        action='store_true', required=False
    )
    parser.add_argument(
        '-mongo_params', '--save_mongo_params', metavar='MONGO_PARAMS',
        help='set connections string with host and port',
        default=['mongodb://192.168.0.20:27017'], type=str, required=False
    )
    parser.add_argument(
        '-cached', '--use_cached_candles',
        help='Use cached data insead of download from server',
        action='store_false', required=False
    )
    parser.add_argument(
        '-v', '--version', action='version',
        version='%(prog)s 0.1.0')

    args = parser.parse_args()

    if not args.strategy and not args.strategy_vwap_aroon and not \
            args.strategy_vwap_ewma and not args.strategy_vwap_momentum:
        print(__author__)
        exit()
    if args.strategy == 'vwap_aroon' or args.strategy_vwap_aroon:
        if args.strategy_vwap_aroon_params is not None:
            if type(args.end_date) is not dt.datetime:
                end_date = dt.datetime(args.end_date)
            else:
                end_date = args.end_date
            bt = Backtester(VWAP_Aroon(
                args.strategy_vwap_aroon_params[0],
                args.strategy_vwap_aroon_params[1],
                args.strategy_vwap_aroon_params[2]),
                args.instrument, args.timeframe, end_date)
            if args.save_plot:
                bt.save_plot = True
            if args.save_mongo:
                bt.save_mongo = True
                bt.mongo_connection = args.save_mongo_params
            if not args.use_cached_candles:
                bt.download = False
    elif args.strategy == 'vwap_momentum' or args.strategy_vwap_momentum:
        if args.strategy_vwap_momentum_params is not None:
            if type(args.end_date) is not dt.datetime:
                end_date = dt.datetime(args.end_date)
            else:
                end_date = args.end_date
            bt = Backtester(VWAP_Momentum(
                args.strategy_vwap_momentum_params[0],
                args.strategy_vwap_momentum_params[1],
                args.strategy_vwap_momentum_params[2]),
                args.instrument, args.timeframe, end_date)
            if args.save_plot:
                bt.save_plot = True
            if args.save_mongo:
                bt.save_mongo = True
                bt.mongo_connection = args.save_mongo_params
            if not args.use_cached_candles:
                bt.download = False
    elif args.strategy == 'vwap_ewma' or args.strategy_vwap_ewma:
        if args.strategy_vwap_ewma_params is not None:
            if type(args.end_date) is not dt.datetime:
                end_date = dt.datetime(args.end_date)
            else:
                end_date = args.end_date
            bt = Backtester(VWAP_EWMA(
                args.strategy_vwap_ewma_params[0],
                args.strategy_vwap_ewma_params[1],
                args.strategy_vwap_ewma_params[2],
                args.strategy_vwap_ewma_params[3]),
                args.instrument, args.timeframe, end_date)
            if args.save_plot:
                bt.save_plot = True
            if args.save_mongo:
                bt.save_mongo = True
                bt.mongo_connection = args.save_mongo_params
            if not args.use_cached_candles:
                bt.download = False
    if args.optimization_params1 is not None:
        for arg in args.optimization_params1:
            if arg is 'None':
                arg = None
        if args.optimization_params2 is not None:
            for arg in args.optimization_params2:
                if arg is 'None':
                    arg = None
        if args.run_optimization:
            bt.optimize(
                ticker=args.optimization_params1[0],
                tf=args.optimization_params1[1],
                min_sl=args.optimization_params2[0],
                min_tp=args.optimization_params2[1],
                max_sl=args.optimization_params2[2],
                max_tp=args.optimization_params2[3],
                steps=args.optimization_params2[4]
                )
        else:
            bt.connect()
