from strategy import strategyLogic
from candles import candleLogic
from __init__ import userVals
import math
import time
from itertools import cycle
import json
from collections import Counter
# Oanda Packages
from oandapyV20 import API
import oandapyV20
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails, TradeCloseRequest
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.trades as trades

class trading():
    # State management
    def __init__(self):
        self.resistance = 0
        self.support = 0
        self.bid = 0
        self.status = "Not Trading"
        self.currentTrade = ""
        self.kill = False # <----- This is a kill switch. If it is true, the bot will shut down.
        # Initialize data channel
        #s = strategyLogic()
        #c = candleLogic()
        #self.data = c.getData()
        #self.volumeData = c.getVol()
        #self.lastVolume = self.volumeData[-1]
        # Initialize Indicators
        #self.currentClose = self.data[-1]
        #self.previousClose
        self.lotSize = ()
        #self.rsi1 = s.manualRSI(self.data, userVals.rsiCount)
        #self.rsi2 = s.talib_rsi(self.data)


    @property
    def getNewData(self):
        c = candleLogic()
        self.data = c.getData()
        return self.data
    

    @property
    def getNewRSI(self):
        s = strategyLogic()
        self.rsi1 = s.manualRSI(t.getNewData, userVals.rsiCount)
        return self.rsi1

    # Check account for open trades
    def getTrades(self):
        r = accounts.AccountDetails(userVals.accountID)
        client = API(access_token=userVals.key)
        rv = client.request(r)
        self.details = rv.get('account')
        return self.details.get('openTradeCount')
    

    # get ticket number of trade
    @staticmethod
    def getTradeID():
        r = trades.OpenTrades(userVals.accountID)
        client = API(access_token=userVals.key)
        rv = client.request(r)
        #print("RESP:\n{} ".format(json.dumps(rv, indent=2)))
        tradeIDs = [o["id"] for o in rv["trades"]]
        return tradeIDs

    @staticmethod
    def getTradeType():
        r = trades.OpenTrades(userVals.accountID)
        client = API(access_token=userVals.key)
        rv = client.request(r)
        lis = []
        dic = {}
        #print("RESP:\n{} ".format(json.dumps(rv, indent=2)))
        #tradeUnits = {o["instrument"]:[o["currentUnits"]] for o in rv["trades"]}
        for key in rv["trades"]:
            dic["instrument"] = key["instrument"]
            dic["units"] = int(key["currentUnits"])
            dic["trade id"] = key["id"]
            #You need to append a copy, otherwise you are just adding references to the same dictionary over and over again
            lis.append(dic.copy())
        return(lis)
        
    
    @staticmethod
    def getCloseableTrades():
        tradingList = []
        lisTrade = t.getTradeType()
        for i in lisTrade:
            if i["instrument"] not in i:
                tradingList.append(i)
        print(tradingList)



        

    # Calculate lot size depending on risk %
    def lots(self, currentBalance):
        #size = 0
        # Different calculation based on trade type
        if self.enterLong() == True:
            return int(float(currentBalance) * 0.35)
        #elif self.enterShort() == True:
        else:
            return int(float(currentBalance) * 0.35)
        #return size

    # Entry/Exit confirmations
    def enterLong(self):
        if all([t.getNewRSI <= 35,
                t.getNewRSI > 25]): return True
        return False



    def enterExtremeLong(self):
        if all([t.getNewRSI <= 25,
                self.getTrades() > 0]): return True
        return False


    def enterShort(self):
        if all([t.getNewRSI >= 65, 
                t.getNewRSI < 75]): return True
        return False
    

    def enterExtremeShort(self):
        if self.rsi1 >= 75: return True
        return False


    def makeTrade(self, mktOrderType):
        api = oandapyV20.API(access_token=userVals.key)
        r = orders.OrderCreate(userVals.accountID, data=mktOrderType)
        api.request(r)


    def getCloseCondition(self):
        if self.getTrades() == 3:
            if all([t.getNewRSI >= 65, ]): return True
            return False
            if all([t.getNewRSI <= 35, ]): return True
            return False
        else:
            return False


    def closeTrade(self):
        units = {"units" : "ALL"}
        client = oandapyV20.API(access_token=userVals.key)
        for i in t.getTradeID():
            ordr = trades.TradeClose(accountID=userVals.accountID, tradeID=i, data=units)
            client.request(ordr)


    # Define closeout
    # def closePosition(self):
    #     if self.currentTrade == "Long":
    #         data = {"longUnits": "ALL"}
    #         client = oandapyV20.API(access_token=userVals.key)
    #         r = positions.PositionClose(accountID=userVals.accountID, instrument=userVals.instrument, data=data)
    #         client.request(r)
    #         print("r: ",r)
    #     elif self.currentTrade == "Short":
    #         data = {"shortUnits": "ALL"}
    #         client = oandapyV20.API(access_token=userVals.key)
    #         r = positions.PositionClose(accountID=userVals.accountID, instrument=userVals.instrument, data=data)
    #         client.request(r)
    #         print("r: ",r)

    
    def tradeCondition(self):
        #sleepTimer = 5 * 60
        sleepTimer = 5
        currentBalance = self.getBalance()
        mktOrderLong = MarketOrderRequest(instrument=userVals.instrument,
                    units=self.lots(currentBalance))
        mktOrderShort = MarketOrderRequest(instrument=userVals.instrument,
                units=(self.lots(currentBalance) *-1))
        
        if all([self.enterLong() == True, 
                float(currentBalance) > 500.00,
                self.getTrades() < 3]): 
            print("entering long")
            print("units: ", self.lots(currentBalance))
            #print("rsi: ",  t.getNewRSI)     
            self.makeTrade(mktOrderLong.data)
            # self.status == "Trading"
            # self.currentTrade == "Long"
            time.sleep(sleepTimer)
        elif all([self.enterShort() == True,
                    float(currentBalance) > 500.00,
                    self.getTrades() < 3]):
            print("entering short")
            print("units: ", self.lots(currentBalance)*-1)
            #print("rsi: ",  t.getNewRSI)  
            self.makeTrade(mktOrderShort.data)
            # self.status == "Trading"
            # self.currentTrade == "Short"
            time.sleep(sleepTimer)
        elif all([self.enterExtremeLong() == True,
                    float(currentBalance) > 500.00,
                    self.getTrades() < 3]):
            print("entering extreme long")
            print("units: ", self.lots(currentBalance))
            self.makeTrade(mktOrderLong.data)
            # self.status == "Trading"
            # self.currentTrade == "Long"
            time.sleep(sleepTimer)
        elif all([self.enterExtremeShort() == True, 
                    float(currentBalance) > 500.00,
                    self.getTrades() < 3]):
            print("entering extreme short")
            print("units: ", self.lots(currentBalance)*-1)
            #print("rsi: ",  t.getNewRSI) 
            self.makeTrade(mktOrderShort.data)                
            # self.status == "Trading"
            # self.currentTrade == "Short"
            time.sleep(sleepTimer)
    
    def getBalance(self):
        h = accounts.AccountDetails(userVals.accountID)
        client = API(access_token=userVals.key)
        hv = client.request(h)
        self.details = hv.get('account')
        currentBalance = self.details.get('marginAvailable')
        print("current balance: ", currentBalance)
        return currentBalance

    # Main trading function
    def main(self): 
        auto_trade = True
        sleepTimer = 5
        sleepTimer2 = 5
        t.getCloseableTrades()
        t.kill == True
'''
        while (auto_trade):
            currentBalance = self.getBalance()
            print("current close: ", t.getNewData[-1])
            print("rsi: ", t.getNewRSI) 
            if float(currentBalance) < 500.00:
                print("insufficient funds")
                print("sleeping..")
                time.sleep(sleepTimer)
                continue
            elif all([self.getTrades() == 0, 
                      float(currentBalance) < 500.00]):
                print("insufficient funds and unable to rebound")
                self.kill = True
            if self.getCloseCondition() == True:
                print("closing trades...")
                self.closeTrade()
            elif self.getTrades() == 3:
                print("Too many trades, wait until queue clears")
                time.sleep(sleepTimer2)
                continue
            else:
                self.tradeCondition()
'''

        # else:
            # if self.currentTrade == "Short":
            #     if self.enterLong() == True:
            #         self.closePosition()
            #         self.status == "Not Trading"
            #         print("Trade Exited")
            #         time.sleep(sleepTimer)
            #     else:
            #         print("No Exits... Looking")
            #         time.sleep(sleepTimer)
            # elif self.currentTrade == "Long":
            #     if self.enterShort() == True:
            #         self.closePosition()
            #         self.status == "Not Trading"
            #         print("Trade Exited")
            #         time.sleep(sleepTimer)
            #     else:
            #         print("No Exits... Looking")
            #         time.sleep(sleepTimer)
            # else:
            #     self.kill = True
            #     print("Error, Closing Down.")
            

    # Run the bot and kill it if kill switch is engaged
if __name__ == "__main__":
    t = trading()
while(t.kill == False):
    t.main()