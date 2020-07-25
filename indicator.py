import math
import numpy as np
import pandas as pd
import ta
from ta.utils import dropna
from supertrend import ST
import argparse

pd.options.mode.chained_assignment = None # This avoids SettingWithCopyWarnings

def read_csv(csv_path):
    data = pd.read_csv(csv_path)
    data = dropna(data)
    data = pd.DataFrame(data.values[::-1], data.index, data.columns)
    return data


def MACD(data, f = 26, s = 12, sign = 9):
	data['MACD'] = ta.trend.macd(data['4. close'], n_fast = 26 , n_slow = 12, fillna = True)
	data['MACD_Signal'] = ta.trend.macd_signal(data['4. close'], n_fast = 26 , n_slow = 12, n_sign = 9, fillna = True)
	macd_buy = (data['MACD_Signal'].shift(1) > data['MACD'].shift(1)) & (data['MACD_Signal'] <= data['MACD'])
	macd_sell = (data['MACD_Signal'].shift(1) < data['MACD'].shift(1)) & (data['MACD_Signal'] >= data['MACD'])
	return macd_buy,macd_sell

def SMA(data,sPeriod = 10,lPeriod = 50):
	data['SMA_l'] = ta.trend.sma_indicator(data['4. close'], n = sPeriod, fillna = True)
	data['SMA_h'] = ta.trend.sma_indicator(data['4. close'], n = lPeriod, fillna = True)
	smaSell = ((data['SMA_l'] <= data['SMA_h']) & (data['SMA_l'].shift(1) >= data['SMA_h'].shift(1)))
	smaBuy = ((data['SMA_l'] >= data['SMA_h']) & (data['SMA_l'].shift(1) <= data['SMA_h'].shift(1)))
	return smaSell,smaBuy

def SuperTrend(data,l=3,h=7):
	data = ST(data,l,h)
	data = dropna(data)
	STSell = (data['SuperTrend'] > data['4. close'])
	STBuy = (data['SuperTrend'] < data['4. close'])
	return STSell,STBuy,data
	

def gen_signal(data):
	m_B,m_S = MACD(data)
	s_B,s_S = SMA(data)
	st_B,st_S,data = SuperTrend(data)
	# data.dropna(inplace = True)
	sigTimeStamps = pd.concat([data['date'],s_S, s_B, st_S,st_B, m_S, m_B],axis=1)
	sigTimeStamps.columns=['Date','SMA Sell','SMA Buy','SuperTrend Sell','SuperTrend Buy','MACD Sell','MACD Buy']
	# signals = sigTimeStamps.loc[sigTimeStamps['SMA Sell'] | sigTimeStamps['SuperTrend Sell'] |sigTimeStamps['MACD Sell'] | sigTimeStamps['SMA Buy'] | sigTimeStamps['SuperTrend Buy'] | sigTimeStamps['MACD Buy']]
	sigTimeStamps.dropna(inplace=True)
	sigTimeStamps['Buy'] = sigTimeStamps['SMA Buy'] & sigTimeStamps['SuperTrend Buy'] & sigTimeStamps['MACD Buy']
	sigTimeStamps['Sell'] = sigTimeStamps['SMA Sell'] | sigTimeStamps['SuperTrend Sell'] | sigTimeStamps['MACD Sell']
	print(sigTimeStamps.tail(4))


parser = argparse.ArgumentParser(description='Generation of Buy/Sell Signal')
parser.add_argument('csv_path',type = str, help = " path too data in csv")
namespace = parser.parse_args()
data = read_csv(**vars(namespace))
# print(data.head(3))
gen_signal(data)

