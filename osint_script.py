import pandas as pd
import matplotlib.pyplot as plt
import re
from user_agents import parse


def collect_data(file):
	lst = []
	pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(\d{2}\/\w{3}\/\d{4}:\d{2}:\d{2}:\d{2}) \+\d{4}\] \"(\w+) ([^ ]+) ([^"]+)\" (\d{3}) (\d+) \"([^"]+)\" \"([^"]+)\" \"([^"]+)\"'
	with open(file, encoding="utf-8") as file:	
		for line in file.readlines():
			match = re.match(pattern, line)
			if match:
				lst.append(match.groups())

	return pd.DataFrame(lst, columns=['ip_address', 'datetime', 'request_type', 'request_uri', 'protocol', 'status_code', 'size', 'referer', 'user_agent', 'something'])


def calculate_stats(df):
	def requests_count(field):
		return df[field].value_counts().to_dict()
	
	def unique_extensions():
		lst = []
		pattern = ".*\.([a-z]{2,}[0-9]*).*"
		for serie in df['request_uri']:
			if "?" in serie:
				serie = serie.split('?')[0]
			match = re.match(pattern, serie)
			if match:
				lst.append(match.groups()[0])
		return list(set(lst))


	return requests_count('ip_address'), unique_extensions(), requests_count('request_type')


def get_browser_family(x):
	try:	
		browser_family = parse(x['user_agent']).browser.family
	except:
		browser_family = "None"
	return browser_family


def is_static(x): 
	file_extension = "None"

	lst_static = ['ttf', 'html', 'jpg', 'json', 'ico', 'woff', 'id', 'woff2', 'png', 'gif', 'css', 'txt']

	pattern = ".*\.([a-z]{2,}[0-9]*).*"
	string = x['request_uri']

	if "?" in string: 
		x = string.split('?')[0]
	match = re.match(pattern, string)
	if match: 
		file_extension = match.groups()[0]

	return "yes" if file_extension in lst_static else "no"


def is_error(x):
	lst = ["400", "403", "404", "499", "500"]
	return "yes" if x['status_code'] in lst else "no"


def show_browser_family(df):
  df['browser_family'].value_counts().plot.bar(legend=True)
	plt.show()


def main():
	file = "10k.log"
	df = collect_data(file)
	ip_req, uniq_ext, http_req = calculate_stats(df)

	df['browser_family'] = df.apply(lambda x: get_browser_family(x), axis=1)
	#show_browser_family(df)

	df['is_static'] = df.apply(lambda x: is_static(x), axis=1)
	
	df['is_error'] = df.apply(lambda x: is_error(x), axis=1)
	#print(df)


if __name__ == "__main__":
	main()
