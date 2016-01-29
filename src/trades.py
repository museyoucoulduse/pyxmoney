class Trades:
    ''' This class stores the trades found by your strategy '''
    def __init__(self):
        self.trdlst = []

    def add_trade(self, index, side, stoploss, takeprofit):
        self.trdlst.append([index, side, stoploss, takeprofit])

    def list_trades(self):
        return self.trdlst

    def clear_trades(self):
        self.trdlst = []
