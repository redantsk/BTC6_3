import time
import pyupbit
import datetime
import numpy as np

access = "your-access"
secret = "your-secret"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_average(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 매도가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_bid_price(ticker):
    """현재 매수가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["bid_price"]

def cur_price(ticker):
    """현재 체결가 조회"""
    return pyupbit.get_current_price(ticker)

def get_odd(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    odd = df.iloc[1]['volume'] / df.iloc[0]['volume']
    return odd

def get_high(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    high_price = df.iloc[0]['high']
    return high_price

def get_target2(ticker, g):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    target2 = df.iloc[0]['open'] * g
    return target2    

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

transaction=0
avg_price=0
k=0.5
sp=0.85
hp=1.1
g=1.05
odd_h=1.1
target_coin=[]
t_coin=[]
tops = ['KRW-MANA', 'KRW-SAND', 'KRW-HUM', 'KRW-BORA', 'KRW-PLA', 'KRW-SOL', 'KRW-CHZ','KRW-ENJ', 'KRW-DKA', 'KRW-CRO', 'KRW-BAT', 'KRW-STORJ', 'KRW-ANKR', 'KRW-WAXP']
odd_tops=[] 
    
# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=60):
            if transaction == 0:
                for p in tops:
                    odd= get_odd(p)
                    if odd > odd_h:
                        odd_tops.append(p)
                        tops.remove(p)

                target_price=[]
                current_price=[]
                comp=[] 
                for n in odd_tops:
                    target = get_target2(n, g)
                    target_price.append(target)
                    current = get_current_price(n)
                    current_price.append(current)
                    comp.append(target < current)

                if any(comp):  
                    buying=[]
                    for ii in list(np.where(comp)[0]):
                        val = pyupbit.get_ohlcv(odd_tops[ii], interval="day", count=1)
                        buying.append((odd_tops[ii], val.iloc[0]['value']))
                    sorted_buying = sorted(buying, key=lambda x:x[1], reverse=True)
                    target_coin=sorted_buying[0][0]
                    t_coin=target_coin[4:]
                    krw = get_balance("KRW")
                    if krw > 999000:
                        upbit.buy_market_order(target_coin, 1000000*0.9995)
                        transaction = 1    
                        avg_price = get_average(t_coin)          

            elif transaction == 1:
                curr_price = cur_price(target_coin)    
                if curr_price < (avg_price * sp):
                    coin_val = get_balance(t_coin)
                    if coin_val > (5000 / curr_price): 
                        upbit.sell_market_order(target_coin, coin_val)  
                    elif coin_val == 0:    
                        transaction = 3
                
                elif curr_price > (avg_price * hp):
                    transaction = 2

            elif transaction == 2:
                high_price=get_high(target_coin)
                curr_price = cur_price(target_coin)    
                if curr_price < ((high_price + avg_price)/2):
                    coin_val = get_balance(t_coin)
                    if coin_val > (5000 / curr_price): 
                        upbit.sell_market_order(target_coin, coin_val)  
                    elif coin_val == 0:    
                        transaction = 3   

        else:
            coin_val = get_balance(t_coin)
            curr_price = cur_price(target_coin) 
            if coin_val > (5000/curr_price): 
                upbit.sell_market_order(target_coin, coin_val)                      
            transaction=0
            avg_price=0
            tops = ['KRW-MANA', 'KRW-SAND', 'KRW-HUM', 'KRW-BORA', 'KRW-PLA', 'KRW-SOL', 'KRW-CHZ','KRW-ENJ', 'KRW-DKA', 'KRW-CRO', 'KRW-BAT', 'KRW-STORJ', 'KRW-ANKR', 'KRW-WAXP']
            odd_tops=[] 
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)