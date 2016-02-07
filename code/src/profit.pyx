import pandas as pd


class Profit:
    ''' Cashier in da bank, who counts for you '''
    def __init__(self, myopt2, trades_list):
        self.trades_list = trades_list
        self.df = myopt2
        self.profit = []
        self.drawdown = []
        self.trades = 0
        self.count_profit()

    def count_profit(self):
        last_trade = 0
        profit = []
        drawdown = 0
        trades = 0

        def _fill_new_last_trade(last_trade, trade):
            last_trade['bid'] = self.df.openBid[trade[0]]
            last_trade['ask'] = self.df.openAsk[trade[0]]
            last_trade['lastindex'] = trade[0]
            last_trade['stoploss'] = trade[2]
            last_trade['takeprofit'] = trade[3]
            return last_trade

        def count_in_last_trade(last_trade, profit, drawdown, trades):
            try:
                trade = self.trades_list[-1]
            except IndexError as e:
                return [0], 0, trades
            if trade[0] < self.df.index[-1]:
                if trade[1] == 'short':
                    trades += 1
                    if last_trade['high'] >= last_trade['bid'] + last_trade['takeprofit']:
                        profit.append(last_trade['takeprofit'])
                        drawdown = (max(drawdown, (abs(last_trade['ask'] - last_trade['low']))))
                    elif last_trade['low'] <= last_trade['bid'] - last_trade['stoploss']:
                        profit.append(-last_trade['stoploss'])
                        drawdown = (max(drawdown, (abs(last_trade['stoploss']))))
                    else:
                        profit.append(self.df.openBid[trade[0]] - last_trade['ask'])
                        drawdown = (max(drawdown, (abs(last_trade['ask'] - last_trade['low']))))
                elif trade[1] == 'long':
                    trades += 1
                    if last_trade['low'] <= last_trade['ask'] - last_trade['takeprofit']:
                        profit.append(last_trade['takeprofit'])
                        drawdown = (max(drawdown, (abs(last_trade['high'] - last_trade['bid']))))
                    elif last_trade['high'] >= last_trade['ask'] + last_trade['stoploss']:
                        profit.append(-last_trade['stoploss'])
                        drawdown = (max(drawdown, (abs(last_trade['stoploss']))))
                    else:
                        profit.append(last_trade['bid'] - self.df.openAsk[trade[0]])
                        drawdown = (max(drawdown, (abs(last_trade['high'] -last_trade['bid']))))
            return profit, drawdown, trades

        for trade in self.trades_list:
            if last_trade == 0:
                last_trade = {
                    'bid': self.df.openBid[self.df.index[0]],
                    'ask': self.df.openAsk[self.df.index[0]],
                    'lastindex': self.df.index[0],
                    'stoploss': trade[2],
                    'takeprofit': trade[3],
                    'high': self.df.highAsk[:trade[0]+1].max(),
                    'low': self.df.lowBid[:trade[0]+1].min(),
                }
            else:
                start = last_trade['lastindex']
                diff = self.df.index[0]
                last_trade = {
                    'bid': last_trade['bid'],
                    'ask': last_trade['ask'],
                    'lastindex': last_trade['lastindex'],
                    'stoploss': last_trade['stoploss'],
                    'takeprofit': last_trade['takeprofit'],
                    'high': self.df.highAsk[start-diff:trade[0]+1-diff].max(),
                    'low': self.df.lowBid[start-diff:trade[0]+1-diff].min()
                }
            if trade[1] == 'short':
                trades += 1
                if last_trade['high'] >= last_trade['bid'] + last_trade['takeprofit']:
                    profit.append(last_trade['takeprofit'])
                    drawdown = (max(drawdown, (abs(last_trade['ask'] - last_trade['low']))))
                elif last_trade['low'] <= last_trade['bid'] - last_trade['stoploss']:
                    profit.append(-last_trade['stoploss'])
                    drawdown = (max(drawdown, (abs(last_trade['stoploss']))))
                else:
                    profit.append(self.df.openBid[trade[0]] - last_trade['ask'])
                    drawdown = (max(drawdown, (abs(last_trade['ask'] - last_trade['low']))))
                last_trade = _fill_new_last_trade(last_trade, trade)
            elif trade[1] == 'long':
                trades += 1
                if last_trade['low'] <= last_trade['ask'] - last_trade['takeprofit']:
                    profit.append(last_trade['takeprofit'])
                    drawdown = (max(drawdown, (abs(last_trade['high'] - last_trade['bid']))))
                elif last_trade['high'] >= last_trade['ask'] + last_trade['stoploss']:
                    profit.append(-last_trade['stoploss'])
                    drawdown = (max(drawdown, (abs(last_trade['stoploss']))))
                else:
                    profit.append(last_trade['bid'] - self.df.openAsk[trade[0]])
                    drawdown = (max(drawdown, (abs(last_trade['high'] -last_trade['bid']))))
                last_trade = _fill_new_last_trade(last_trade, trade)
        profit, drawdown, trades = count_in_last_trade(last_trade, profit, drawdown, trades)

        self.profit = profit
        self.drawdown = -drawdown/self.total_profit()
        self.trades = trades

    def profit_list(self):
        return self.profit

    def cumsum_profit(self):
        return pd.DataFrame(self.profit).cumsum()

    def total_profit(self):
        return pd.DataFrame(self.profit).sum().values[0]

    def max_drawdown(self):
        return -abs(self.drawdown*100)

    def actual_prices(self):
        return self.df['closeBid']
