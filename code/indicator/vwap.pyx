class VWAP():
    ''' Calculates Volume Weighted Average Price '''
    def __init__(self, df):
        self.df = df.copy()

    def caluculate(self):
        self.df['Cum_Vol'] = self.df['volume'].cumsum()
        try:
            self.df['Cum_Vol_Price'] = (self.df['volume'] *
                                   (self.df['highMid'] + self.df['lowMid'] +
                                   self.df['closeMid'] ) /3).cumsum()
        except:
            self.df['Cum_Vol_Price'] = (self.df['volume'] *
                                   ((self.df['highBid'] + self.df['highAsk']) / 2 +
                                   (self.df['lowBid'] + self.df['lowAsk']) / 2 +
                                   (self.df['closeBid'] + self.df['closeAsk']) / 2) /3).cumsum()
        finally:
            self.df['vwap'] = self.df['Cum_Vol_Price'] / self.df['Cum_Vol']

        return self.df['vwap']
