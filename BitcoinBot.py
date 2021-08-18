import cbpro, time, threading, pickle
from dotenv import load_dotenv
import os 

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
API_PASS = os.getenv('API_PASS')

FLOOR_PRICE = 46000 #If no bitcoin has been bought, then start buying at this price
BITCOIN_TRADE_FLOOR = 0.001 #Smallest amount of bitcoin that you can trade on coinbase
COINBASE_FEE = 0.005
BUY_MULTIPLIER = COINBASE_FEE + 0.004
SELL_MULTIPLIER = COINBASE_FEE + 0.005

btc_id = '43f7fd86-a998-4e82-8619-cad7b0b76fc5'
usd_id = 'f2a65231-2013-49df-8918-65a0cb52540d'

# Fetch database of trade data
bids = {}
asks = {}
bidsFile = open("bids_file.pkl", "rb")
bids = pickle.load(bidsFile)
asksFile = open("asks_file.pkl", "rb")
bids = pickle.load(asksFile)

#auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)
# Use the sandbox API (requires a different set of API access credentials)
auth_client = cbpro.AuthenticatedClient(API_KEY, API_SECRET, API_PASS,
api_url="https://api-public.sandbox.pro.coinbase.com")
public_client = cbpro.PublicClient()

#Gets Price of coin
def getCoinPrice(coin = 'BTC-USD'):
    return public_client.get_product_order_book(coin)['asks'][0][0]

#Buy Bitcoin
def buy_Bitcoin(coin_price, amount):
    
    auth_client.place_limit_order(product_id='BTC-USD', 
                              side='buy', 
                              price = str(coin_price*amount),
                              size=str(amount))
    print("Bought", amount, "bitcoin at $" ,coin_price, "for $" , str(coin_price)*amount)

def sell_bitcoin(coin_price, amount):
    auth_client.place_limit_order(product_id='BTC-USD', 
                              side='sell', 
                              price = str(coin_price*amount),
                              size=str(amount))
    print("Sold", amount, "bitcoin at $" ,coin_price, "for $" , str(coin_price)*amount)

def printasks():
    print(asks)

def printbids():
    print(bids)

def printaccount():
    try:
        print("Bitcoin available for trade: ", auth_client.get_account(btc_id)["available"])
        print("USD available for trade: ", auth_client.get_account(usd_id)["available"])
        print("Bitcoin price: $", getCoinPrice('BTC-USD'))
    except:
        print('print account failed')

class DoThis(threading.Thread):
    def __init__( self ):
        threading.Thread.__init__( self )
        self.stop = False

    # run is where the dothis code will be
    def run( self ):
        while not self.stop:
            # Loop this infinitely until I tell it stop
            time.sleep(10)
            updated_coin_price = float(getCoinPrice('BTC-USD'))
            print(updated_coin_price)
            usd_funds = float(auth_client.get_account(usd_id)["available"])
            bitcoin_funds = float(auth_client.get_account(btc_id)["available"])

            #Get previous price of bitcoin sold for
            #buy bitcoin for updated_coin_price if a profit can be made
            #Add to bidslist adn remove from asks list
            if usd_funds*updated_coin_price*0.001*(1+COINBASE_FEE) < float(auth_client.get_account(usd_id)["available"]):
                if asks != {}:
                    min_Price = min(asks.keys()) #If current price > previous price by % +0.5% (coinbase fee) (or price floor) then

                    if updated_coin_price <= min_Price*(1-BUY_MULTIPLIER): #Sell Amount of bitcoin that was bought for certain price or Sell 2.5%
                        if asks[min_Price] >= 0.002:
                            min_Amount = 0.001
                            asks[min_Price] -= 0.001
                        else:
                            min_Amount = asks[min_Price]
                            del asks[min_Price]

                        buy_Bitcoin(updated_coin_price, min_Amount)

                        if updated_coin_price in bids.keys():
                            bids[updated_coin_price] += min_Amount
                        else:    
                            bids[updated_coin_price] = min_Amount

                else:
                    min_Price = FLOOR_PRICE    
                    if updated_coin_price <= min_Price*(1-BUY_MULTIPLIER):
                        buy_Bitcoin(updated_coin_price, 0.001)
                        bids[updated_coin_price] = 0.001

            # If selling btc can make a profit then do so.    
            if bids != {} and bitcoin_funds >= 0.001:
                min_sell_Price = min(bids.keys())
                if updated_coin_price > min_sell_Price*(1+SELL_MULTIPLIER):

                    if bids[min_sell_Price] >= 0.002:
                        min_Amount = 0.001
                        bids[min_sell_Price] -= 0.001
                    else:
                        min_Amount = bids[min_sell_Price]
                        del bids[min_sell_Price]

                    if updated_coin_price in asks.keys():
                        asks[updated_coin_price] += min_Amount
                    else:    
                        asks[updated_coin_price] = min_Amount

                    sell_bitcoin(updated_coin_price, min_Amount)

#Console loop, bitcoin bot will run until told to stop
console_running = True
a = None
while console_running:
    command = input("Enter command:")

    if command == "start":
        a = DoThis()
        a.start()
    if command == "stop":
        a.stop = True
        a.join()
        a = None
    if command == "bids":
        printbids()
    if command == "asks":
        printasks()   
    if command == "account":
        printaccount()   
    if command == "quit":
        console_running = False

#Save asks and bids to pkl file
bidsFile = open("bids_file.pkl", "wb")
pickle.dump(bids, bidsFile)
bidsFile.close()
asksFile = open("asks_file.pkl", "wb")
pickle.dump(bids, asksFile)
asksFile.close()
