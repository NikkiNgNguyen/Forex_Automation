import requests as r
import numpy as np
from __init__ import userVals

from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments

class user1():
    client = API(access_token=userVals.key)
    o = instruments.InstrumentsCandles(instrument=userVals.instrument,
        params = userVals.params)

class candleLogic:
    def OHLC(self, data):
        # Call imported user1 class
        user1.client.request(user1.o)
        candles = user1.o.response.get("candles")
        candleData = candles[data].get("mid")
        # OHLC variables to return in array
        o = candleData.get("o")
        h = candleData.get("h")
        l = candleData.get("l")
        c = candleData.get("c")
        return float(o), float(h), float(l), float(c)

    def vol(self, volumeData):
        # Call imported user1 class
        user1.client.request(user1.o)
        candles = user1.o.response.get("candles")
        volData = candles[volumeData]
        v = volData.get("volume")
        return int(v)
    
    def Volume(self, volumeData):
        return self.vol(volumeData)

    
    def getVol(self):
        volList = []
        for x in range(0, userVals.count):
            volList.append(self.Volume(x))
        return volList

    # Define clean function routes for returning proper data
    def Open(self, data):
        return self.OHLC(data)[0]
    
    def High(self, data):
        return self.OHLC(data)[1]
    
    def Low(self, data):
        return self.OHLC(data)[2]

    def Close(self, data):
        return self.OHLC(data)[3]
    
    def getData(self):
        numList = []
        for x in range(0, userVals.count):
            numList.append(self.Close(x))
        return numList