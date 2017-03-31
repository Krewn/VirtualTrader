
from yahoo_finance import Share
from FSaaDb import dbHandle
from datetime import datetime

def makeButton():
    print("todo")

class portfolio:
    def __init__(self):
        initalVars = dir(self)
        self.evaluations = []
        self.tradeHistory = []
        self.holdings = {}
        self.lastKnowPrices = {}
        self.repository = ""
        self.cash = 10000
        self.Variables = list(set(dir(self)).difference(set(initalVars)))
        self.fsdb = dbHandle(".VTrader.FSaaDB")
        self.tradingFee = 0

    def save(self):
        v = {}
        for k in self.Variables:
            exec("v['"+k+"']=self."+k)
        self.fsdb.dump(v)

    def load(self):
        values = self.fsdb.read(self.fsdb.root)
        for k in values:
            exec("self."+k+"=values['"+k+"']")

    def evaluate(self):
        value = self.cash
        for k in self.holdings:
            try:
                value += float(self.quote(k,n=3)[1])*self.holdings[k]
            except:
                value += float(self.lastKnowPrices[k]) * self.holdings[k]
        self.evaluations.append(value)
        return(value)

    def holdingSummary(self):
        value = self.cash
        summaryHead = "\nCash:\t" + str(self.cash) + "\n"
        summary = ""
        total = 0
        summary += "Tag" + "\t" + "Quantity" + "\t" + "Value" + "\n"
        for k in self.holdings:
            try:
                value = float(self.quote(self.holdings[k],n=3)[1])*self.holdings[k]
            except:
                value = float(self.lastKnowPrices[k]) * self.holdings[k]
            summary += k+"\t"+k+"\t\t"+str(value)+"\n"
            total += value
        summaryHead += "Stocks:\t" + str(total)+"\n"
        summaryHead += "Total:\t" + str(total+self.cash)+"\n\n"
        return(summaryHead+summary+"\n")

    def order(self,tag,quantity,cp=True):
        try:
            aQuote = float(self.quote(tag)[1])
        except:
            print("Order failed:"+str([tag,quantity])+"-Unable To Obtain Price.")
            return()
        print(aQuote)
        transactionCost = aQuote*quantity
        if(transactionCost > self.cash):
            print("Order failed:" + str([tag, quantity]) + "-Insufficient Funds")
            return()
        if not(tag in self.holdings.keys()):
            self.holdings[tag]=0
        if(self.holdings[tag] < quantity*-1):
            print("Order failed:" + str([tag, quantity]) + "-Insufficient Holdings")
            return()
        self.holdings[tag] += quantity
        self.cash -= transactionCost
        self.tradeHistory.append([quantity,tag,transactionCost,str(datetime.now())])
        if(cp):
            self.save()
        return()

    def batchOrder(self,inputFile,depth=None,funds=None,qFunc = lambda nOptions,place,mmin,mmax,f=lambda x :1. : f(mmin+(mmax-mmin)*(place)/nOptions)):
        fh = open(inputFile,"r")
        orderOptionsinfo = [o for o in [k.split("\t") for k in fh.read().split("\n")]]
        orders = []
        depth = depth if depth!=None else len(orderOptionsinfo)/7 # 7 is my lucky number...
        normalizedQuantites = [qFunc(depth,k,0,0) for k in range(0,depth)]
        nsum = sum(normalizedQuantites)
        funds = funds if funds != None else self.cash
        normalizedQuantites = [funds*(k/nsum) for k in normalizedQuantites]
        orders = []
        for n,k in enumerate(normalizedQuantites):
            try:
                self.order(orderOptionsinfo[n][0],int(normalizedQuantites/self.quote(orderOptionsinfo[n][0])))
            except:
                print(k+" unavailible for trading.")
        self.save(self)

    def liquidate(self,shares = None):
        shares = shares if shares != None else self.holdings
        for k in shares:
            self.order(k,-1*shares[k])

    def quote(self, tag, n=3):
        try:
            stock = Share(tag)
            p = stock.get_price()
            t = stock.get_trade_datetime()
            self.lastKnowPrices[tag] = p
            return ([t, p])
        except:
            if (n > 0):
                return (self.quote(tag, n=n - 1))
            else:
                return(self.lastKnowPrices[tag])

    def setRepo(self):
        print("todo")

    def pushTrades(self):
        print("todo")

def UI():
    myPortfolio = portfolio()
    myPortfolio.load()
    task = ""
    while(task!="end"):
        task = input("Task :")
        if (task == "order"):
            tag = input("tag :")
            quantity = input("quantity :")
            print(myPortfolio.order(tag,float(quantity)))
        if (task == "statement"):
            print(myPortfolio.holdingSummary())
    myPortfolio.evaluate()
    myPortfolio.save()
    print("Goodbye!")
