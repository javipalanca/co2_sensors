import datetime

import pandas as pd
from prophet import Prophet


class Predictor(object):
	def __init__(self, dates, values):
		self.dates = dates
		self.values = values
		self.model = None
		self.df = pd.DataFrame({'ds': self.dates, 'y': self.values})
		# remove last row if y == 0
		if float(self.df.iloc[-1]['y']) == 0:
			self.df = self.df[:-1]

	def predict(self, days):
		if not self.model:
			self.fit()
		future = self.model.make_future_dataframe(periods=days)

		forecast = self.model.predict(future)
		# df column to list
		dates = [str(datetime.datetime.fromtimestamp(d / 1000000000).date()) for d in forecast['ds'].values.tolist()]
		values = forecast['yhat'].values.tolist()
		return dates, values

	def fit(self):
		self.model = Prophet()
		self.model.fit(self.df)
