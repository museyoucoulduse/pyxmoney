class Instruments:
    ''' Connect to Oanda and get all instruments and respective pip point'''
    def __init__(self, oanda_client):
        self.client = oanda_client
        self.raw_inst_list = self.client.get_instruments()
        self.instruments = self.get_instruments()
        self.pips = self.get_pips()

    def get_instruments(self):
        instruments = self.raw_inst_list
        instlst = []
        [instlst.append(ins['instrument']) for ins in instruments['instruments']]
        return instlst

    def get_pips(self):
        instruments = self.raw_inst_list
        piplst = []
        [piplst.append(ins['pip']) for ins in instruments['instruments']]
        return piplst
