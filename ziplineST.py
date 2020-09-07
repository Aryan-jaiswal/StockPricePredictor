import pytz
from datetime import datetime
from zipline.api import order, symbol, record, order_target
from zipline.algorithm import TradingAlgorithm
from zipline.data import bundles
import numpy as np
from trading_calendars import register_calendar, get_calendar

# cal = get_calendar('NYSE')

# import pandas as pd

# bundle_name = 'quandl' # "a bundle name"
# ticker_name = "IBM"
# end_date = pd.Timestamp.utcnow()
# calendar_name = 'NYSE' # "the calendar name"
# window=200 # how many days you want to look back

# bundle_data = bundles.load(bundle_name)
# data_por = DataPortal(bundle_data.asset_finder, 
#                       get_calendar(calendar_name),
#                       bundle_data.equity_daily_bar_reader.first_trading_day,
#                       equity_minute_reader=bundle_data.equity_minute_bar_reader,
#                       equity_daily_reader=bundle_data.equity_daily_bar_reader,
#                       adjustment_reader=bundle_data.adjustment_reader)

# sym = data_por.asset_finder.lookup_symbol(ticker_name, end_date)
# data = data_por.get_history_window(assets=[sym],
#                                    end_dt=end_date,
#                                    bar_count=window,
#                                    frequency='1d',
#                                    data_frequency='daily'
#                                    ,field='close'
#                                    )
# print(data)
# %%zipline --start 2014-1-1 --end 2018-1-1 -o dma.pickle

def initialize(context):
	context.i = 0
	context.asset = symbol('AAPL')


def handle_data(context, data):

	n = 7
	f = 3
	context.i += 1
	# if context.i < n:
	#   return

	df = data.history(context.asset, ['price', 'open', 'high', 'low', 'close', 'volume'], bar_count=10, frequency="1d")
	df['H-L']=abs(df['high']-df['low'])
	df['H-PC']=abs(df['high']-df['close'].shift(1))
	df['L-PC']=abs(df['low']-df['close'].shift(1))
	df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1)
	df.dropna(inplace = True)
	df['ATR']=np.nan
	df.ix[n-1,'ATR']=df['TR'][:n-1].mean() 
	for i in range(n,len(df)):
		df['ATR'][i]=(df['ATR'][i-1]*(n-1)+ df['TR'][i])/n

	#Calculation of SuperTrend
	df['Upper Basic']=(df['high']+df['low'])/2+(f*df['ATR'])
	df['Lower Basic']=(df['high']+df['low'])/2-(f*df['ATR'])
	df['Upper Band']=df['Upper Basic']
	df['Lower Band']=df['Lower Basic']
	for i in range(n,len(df)):
		if df['close'][i-1]<=df['Upper Band'][i-1]:
			df['Upper Band'][i]=min(df['Upper Basic'][i],df['Upper Band'][i-1])
		else:
			df['Upper Band'][i]=df['Upper Basic'][i]    
	for i in range(n,len(df)):
		if df['close'][i-1]>=df['Lower Band'][i-1]:
			df['Lower Band'][i]=max(df['Lower Basic'][i],df['Lower Band'][i-1])
		else:
			df['Lower Band'][i]=df['Lower Basic'][i]

	df['SuperTrend']=np.nan
	for i in df['SuperTrend']:
		if df['close'][n-1]<=df['Upper Band'][n-1]:
			df['SuperTrend'][n-1]=df['Upper Band'][n-1]
		elif df['close'][n-1]>df['Upper Band'][i]:
			df['SuperTrend'][n-1]=df['Lower Band'][n-1]
	for i in range(n,len(df)):
		if df['SuperTrend'][i-1]==df['Upper Band'][i-1] and df['close'][i]<=df['Upper Band'][i]:
			df['SuperTrend'][i]=df['Upper Band'][i]
		elif  df['SuperTrend'][i-1]==df['Upper Band'][i-1] and df['close'][i]>=df['Upper Band'][i]:
			df['SuperTrend'][i]=df['Lower Band'][i]
		elif df['SuperTrend'][i-1]==df['Lower Band'][i-1] and df['close'][i]>=df['Lower Band'][i]:
			df['SuperTrend'][i]=df['Lower Band'][i]
		elif df['SuperTrend'][i-1]==df['Lower Band'][i-1] and df['close'][i]<=df['Lower Band'][i]:
			df['SuperTrend'][i]=df['Upper Band'][i]   
	
	print(df['SuperTrend'])
	# Trading logic
	if (df.ix[len(df)-1,'SuperTrend'] < df.ix[len(df)-1,'close']):
		print('bought')
		# order_target orders as many shares as needed to
		# achieve the desired number of shares.
		order_target(context.asset, 100)
	elif (df.ix[len(df)-1,'SuperTrend'] > df.ix[len(df)-1,'close']):
		order_target(context.asset, 0)


	# Save values for later inspection
	record(AAPL=data.current(context.asset, ['price', 'open', 'high', 'low', 'close', 'volume']), SuperTrend = df['SuperTrend'])

