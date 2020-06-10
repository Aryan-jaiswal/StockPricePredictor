from alpha_vantage.timeseries import TimeSeries
import json
import argparse

#2FHBXTFLLMDMDSM7
def save_dataset(symbol,t_ind):

	key = json.load(open('key.json', 'r'))
	ts = TimeSeries(key = key ,output_format = 'pandas')
	# data,metadata = ts.get_daily(symbol = symbol, outputsize = 'full')
	with open(symbol+'_daily.csv','w') as file:
		data.to_csv(path_or_buf = file)

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument('symbol',type = str, help = " symbol")
	parser.add_argument('--t_ind', type = str, choices = ['SMA','EMA'], nargs = '?', help = "Specify the Technical Indicator you want to use")
	namespace = parser.parse_args()
	save_dataset(**vars(namespace))