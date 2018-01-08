#####################################################
#       Crypto Price Alert Script                   #
#                                                   #
# Author  : Vikas Shakya                            #
# Email   : vikasshakya00@gmail.com                 #
#####################################################

import requests
from win32api import *
from win32gui import *
import win32con
import sys, os, re
import time, random
import operator

 
class WindowsBalloonTip:
    def __init__(self, title, msg):
        message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
        }
        
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"       
        wc.lpfnWndProc = message_map 
        classAtom = RegisterClass(wc)       
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU        
        self.hwnd = CreateWindow( classAtom, "Taskbar", style, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0, hinst, None)        
        UpdateWindow(self.hwnd)
        iconPathName = os.path.abspath(os.path.join( sys.path[0], "icon\\bitcoin.ico" ))        
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        
        try:
           hicon = LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
        except Exception,e:
          print e
          hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "Crypto")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY,(self.hwnd, 0, NIF_INFO, win32con.WM_USER+20, hicon, "Balloon Crypto",msg,200,title))        
        time.sleep(30)
        DestroyWindow(self.hwnd)
        UnregisterClass(classAtom, hinst)
    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)

def balloon_tip(title, msg):
    w=WindowsBalloonTip(title, msg)





def add_comma(amount):
    orig = amount
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', amount)
    if orig == new:
        return new
    else:
        return add_comma(new)

    

def koinex():
    msg = "\n"
    try:
        req = requests.get('https://koinex.in/api/ticker') 
        req = req.json()
        prices = req['prices']
        for price in prices:
            if price == "BTC" or price == "ETH" or  price == "XRP" :
                msg = msg + price + "/INR :  " + add_comma(str(prices[price])) + "\n"       
    except Exception,e:
          print e
    return str(msg)




def bittrex():
    msglist = ['None']
    msg = "\n"
    try:
        req = requests.get('https://bittrex.com/api/v1.1/public/getmarketsummaries') 
        req = req.json()
        results = req['result']
        msg = msg + "Coin\tPrice[sats]\t%Change\n----\t-----------\t--------\n"
        for result in results:
            if result['MarketName'] == "BTC-XRP" or result['MarketName'] == "BTC-XVG" or\
               result['MarketName'] == "BTC-XLM" or result['MarketName'] == "BTC-TRX" or\
               result['MarketName'] == "BTC-POWR" or result['MarketName'] == "BTC-OMG" or\
               result['MarketName'] == "BTC-NEO" or result['MarketName'] == "BTC-NXT" or\
               result['MarketName'] == "BTC-ADA" or result['MarketName'] == "BTC-ARK":
                per = ((result['Last'] - result['PrevDay'])/ result['Last']) * 100
                per = add_comma("{0:.1f}".format(per))
                msg = msg + result['MarketName'].split("-")[-1] + "\t" + add_comma("{0:.8f}".format(result['Last'])) + "\t" + str(per) + "%\n"
                m = "\n" + result['MarketName'] + ":\n-----------\n" + \
                      "Price : " + add_comma("{0:.8f}".format(result['Last'])) + " sats\t[" + str(per) + "%]" + \
                      "\n\nOpenBuyOrders : " + str(result['OpenBuyOrders']) + \
                      "\nOpenSellOrders : " + str(result['OpenSellOrders']) + \
                      "\n\nLow : " + add_comma("{0:.8f}".format(result['Low'])) + \
                      "\tBid : " + add_comma("{0:.8f}".format(result['Bid'])) + \
                      "\nHigh : " + add_comma("{0:.8f}".format(result['High'])) + \
                      "\tAsk : " + add_comma("{0:.8f}".format(result['Ask'])) + "\n"
                msglist.append(m)
        msglist[0] = msg           
          
                     
    except Exception,e:
          print e
    return msglist





def CMC():
    msg = []
    msg1 = "\n"
    msg2 = "\nBiggest Gainers in 24h:\n\nRank\tCoin\t%24h\n-----\t-----\t------\n"
    msg3 = "\nBiggest Losers in 24h:\n\nRank\tCoin\t%24h\n-----\t-----\t------\n"
    msg4 = "\nBiggest Gainers in 1h:\n\nRank\tCoin\t%1h\n-----\t-----\t------\n"
    msg5 = "\nBiggest Losers in 1h:\n\nRank\tCoin\t%1h\n-----\t-----\t------\n"  
    dic1 = {}
    dic2 = {}
    try:
        req1 = requests.get('https://api.coinmarketcap.com/v1/global/') 
        req1 = req1.json()             
        req2 = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=1500')
        req2 = req2.json()        
        for r in req1:
            if r == "total_market_cap_usd":
                msg1 = "\nTMC : $ " + add_comma("{0:.1f}".format(req1[r])) + msg1
            elif r == "bitcoin_percentage_of_market_cap":
                msg1 = msg1 + "BTC Share : " + str(req1[r]) + "%\n\n"
            else:
                continue
        msg1 = msg1 + "Coin\tPrice\t\t%24h\n----\t----\t\t----\n"
        for r in req2:           
            if r['symbol'] == "BTC" or r['symbol'] == "ETH" or r['symbol'] == "XRP" \
               or r['symbol'] == "ADA" or r['symbol'] == "TRX" or r['symbol'] == "XVG" \
               or r['symbol'] == "POWR" or r['symbol'] == "LEND":                
                msg1 = msg1 + r['symbol'] + "\t$ " + add_comma(r['price_usd']) + "\t" +str("{0:.1f}".format( float(r['percent_change_24h']))) + "%\n"
                if r['percent_change_24h']!= None:
                    dic1[r['rank'] + "\t" + r['symbol']] = float(r['percent_change_24h'])
                if r['percent_change_1h']!= None:
                    dic2[r['rank'] + "\t" + r['symbol']] = float(r['percent_change_1h'])
            else:
                if r['percent_change_24h']!= None:
                    dic1[r['rank'] + "\t" + r['symbol']] = float(r['percent_change_24h'])
                if r['percent_change_1h']!= None:
                    dic2[r['rank'] + "\t" + r['symbol']] = float(r['percent_change_1h'])
                    
        sorted_asc1 = sorted(dic1.items(), key=operator.itemgetter(1))
        sorted_des1 = sorted(dic1.items(), key=operator.itemgetter(1), reverse=True)
        sorted_asc2 = sorted(dic2.items(), key=operator.itemgetter(1))
        sorted_des2 = sorted(dic2.items(), key=operator.itemgetter(1), reverse=True)
        
        for i in xrange(10):
            msg2 = msg2 + sorted_des1[i][0] + "\t" + str("{0:.1f}".format(sorted_des1[i][1])) + "%\n"
            msg3 = msg3 + sorted_asc1[i][0] + "\t" + str("{0:.1f}".format(sorted_asc1[i][1])) + "%\n"
            msg4 = msg4 + sorted_des2[i][0] + "\t" + str("{0:.1f}".format(sorted_des2[i][1])) + "%\n"
            msg5 = msg5 + sorted_asc2[i][0] + "\t" + str("{0:.1f}".format(sorted_asc2[i][1])) + "%\n"
            
         
        msg = [msg1,msg2,msg3,msg4,msg5]  
    except Exception,e:
          print e    
    return msg






def Exchange(api,coin,fiat):
    msg = "\n"
    try:
        req = requests.get(api)        
        req = req.json()        
        for r in req:
            if r == "last_traded_price" or r == "last_price":    
                msg = "\n" + coin + " :  " + fiat + " " + add_comma(str(req[r])) + msg
            elif r == "ask" or r == "bid":
                msg = msg + str(r).capitalize() + " :  " + fiat + " " + add_comma(str(req[r]))  + "\n"
            else:
                continue
    except Exception,e:
          print e
    return str(msg)






if __name__ == "__main__":
    
    while True:
        try:
            exchange = {"BitFinex":["https://api.bitfinex.com/v1/pubticker/btcusd","BTC","$"],
                        #"BtcxIndia":["https://api.btcxindia.com/ticker/","XRP","INR"],
                        "EthexIndia":["https://api.ethexindia.com/ticker/","ETH","INR"]                                                
                        }
            
            
            msg = CMC()
            for m in msg:
                print "CMC Price Alert:\n" + m
                balloon_tip("CMC Price Alert", m)
                time.sleep(random.randint(2,5))
                
            
            msg = koinex()
            print "Koinex Price Alert:\n" + msg
            balloon_tip("Koinex Price Alert", msg)    
            time.sleep(random.randint(2,5))
            

            msg = bittrex()            
            for m in msg:
                print "Bittrex Price Alert:\n" + m
                balloon_tip("Bittrex Price Alert", m)    
                time.sleep(random.randint(2,5))
                

            for ex in exchange:        
                msg = Exchange(exchange[ex][0],exchange[ex][1],exchange[ex][2])
                print ex +" Price Alert:\n" + msg
                balloon_tip(ex +" Price Alert", msg)    
                time.sleep(random.randint(2,5))           
                           
            
            time.sleep(random.randint(600,900))      # Notification Time-interval (in seconds)
            

        except (KeyboardInterrupt, SystemExit):
            raise


  


