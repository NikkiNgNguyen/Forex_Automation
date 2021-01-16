import numpy as np
#import talib

# Strategy logic & indicators go here
class strategyLogic():
    def SMA(self, prices, length, period):
        return sum(prices[(length-period):length]) / period

    def SMAprev(self, prices, length, period):
        return sum(prices[(length-period-1):length-1]) / period

    def manualRSI(self, prices, length):
        
        deltas = np.diff(prices)
        seed = deltas[:length+1]
        up = seed[seed >= 0].sum()/length
        down = -seed[seed < 0].sum()/length
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:length] = 100. - 100./(1. + rs)
        #rsi = 100. -100./(1. + rs)
        #for i in range(length, len(prices)):
        for i in range(len(prices)):
            delta = deltas[i-1] # The diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            
            up = (up*(length-1) + upval)/length
            down = (down*(length-1) + downval)/length

            rs = up/down
            #rsi[i] = 100. -100./(1. + rs)
            rsi = 100. -100./(1. + rs)
            
        #rsi = 35
        return rsi

    # def talib_rsi(self, prices):
    #     priceList = np.asarray(prices, dtype='f8')   
    #     rsiList = talib.RSI(priceList, timeperiod = 14)
    #     return rsiList[-1]