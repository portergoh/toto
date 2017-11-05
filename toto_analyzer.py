#!/usr/bin/env pythonw

import requests
import time
import subprocess
import json
import argparse
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from wordcloud import WordCloud
from datetime import datetime
from pprint import pprint

SLEEP_TIME = 1

def is_record_exist(date, file_path):
        cmd = "grep -w '{}' {}".format(date,file_path)
        try:
                output = subprocess.check_output(cmd,shell=True)
                if output:
                        return True
        except:
                return False

def write_record_to_cache(record,file_path):
	cmd = "echo {} >> {}".format(record,file_path)
	output = subprocess.check_output(cmd,shell=True)

def get_page_source(url):
	driver = webdriver.Firefox()
        driver.get(url)
        page_source = driver.page_source.encode('utf-8')
	return page_source

def get_result_content(url):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	page_source = requests.get(url,headers=headers).content
	#page_source = get_page_source(url)
	result_detail = BeautifulSoup(page_source,"html.parser")
	return result_detail

def get_winning_numbers(page_detail):
	winning_numbers = []
	for i in range(1,7):
		win_tag = page_detail.find("td", {"class":"win{}".format(i)})
		if win_tag:
			winning_numbers.append(win_tag.get_text().encode("utf8"))
	return winning_numbers

def get_past_results(url,update_from_sgpool=False):
	data_path = ".cache"
    	lottery_results = {}

	if update_from_sgpool:
		page_source = get_page_source(url.strip())
    		soup = BeautifulSoup(page_source,"html.parser")
    		options = soup.find_all("option", {"winningsharesuploaded": "True"})
		for option in options:
			retry = True
			list_of_winning_nums = []
        		url_parameter =  option.get("querystring")
        		http_url = url + "?" + url_parameter
			lottery_date = option.get_text().encode("utf8")
			# retrieve records from internet and write to cache
			if (not is_record_exist(lottery_date, data_path)):
				while retry:
					time.sleep(SLEEP_TIME)
        				result_detail = get_result_content(http_url.strip())
        				list_of_winning_nums = get_winning_numbers(result_detail)
					if len(list_of_winning_nums) > 0:
						record = lottery_date + "," + " ".join(str(x) for x in list_of_winning_nums)
						write_record_to_cache(record, data_path)
						retry = False
					else:
			   			retry = True
				print(lottery_date,list_of_winning_nums)

	# retrieve results from cache
	lottery_results = read_dict_from_cache(data_path)
	return lottery_results

def read_dict_from_cache(path):
	dict_of_results = {}
	with open(path, "r") as fint:
		for line in fint:
			split_str = line.split(",")
			date = split_str[0] + "," + split_str[1]
			dict_of_results[date] = split_str[2]
	return  dict_of_results

def compute_num_frequency(num_row_list):
	list_of_num = []
	dict_of_num_freq = {}
	for num_row in num_row_list:
		num_row_split = num_row.split()
		for num in num_row_split:
			list_of_num.append(num)

	for num in list_of_num:
		if num in dict_of_num_freq:
			dict_of_num_freq[num] += 1
		else:
			dict_of_num_freq[num] = 1

	#for k,v in dict_of_num_freq.items():
	#	print ("{} - {}".format(k,v))

	return dict_of_num_freq

def generate_num_cloud(dict_of_num_freq):
	numcloud = WordCloud().generate_from_frequencies(frequencies=dict_of_num_freq)
	plt.imshow(numcloud, interpolation ='bilinear')
	plt.axis("off")
	plt.show()

def get_last_drawn_num_rows(dict_of_results,num):
	selected_num_rows = []
	sorted_keys = sorted(dict_of_results.iterkeys(),key=lambda x: datetime.strptime(x, "%a, %d %b %Y"),reverse=True)
	for key in sorted_keys[0:num]:
		selected_num_rows.append(dict_of_results[key])
	return sorted_keys,selected_num_rows

if __name__ == "__main__":
	url = "http://www.singaporepools.com.sg/en/product/Pages/toto_results.aspx"
	# read first from cache, if cache does not have, fetch from internet
	retrieve_updates_from_internet = False
	parser = argparse.ArgumentParser()
	parser.add_argument("--plotfreq",
				help="plot the number occurance using word cloud",
				action="store_true")

	parser.add_argument("--update",
				help="update the local cache with latest records from Singapore Pool",
				action="store_true")

	parser.add_argument("-d", "--draw", type=int,
                    help="return the last number of draws based of user input")

	args = parser.parse_args()
        if args.update:
		retrieve_updates_from_internet = True

	dict_of_results = get_past_results(url,retrieve_updates_from_internet)
        if (args.plotfreq) & (args.draw is None):
		dict_of_num_freq = compute_num_frequency(dict_of_results.values())
		generate_num_cloud(dict_of_num_freq)

	if (args.plotfreq) & (args.draw is not None):
		dates,list_of_draws = get_last_drawn_num_rows(dict_of_results,args.draw)
		dict_of_num_freq = compute_num_frequency(list_of_draws)
                generate_num_cloud(dict_of_num_freq)

	if args.draw is not None:
		dates,list_of_draws = get_last_drawn_num_rows(dict_of_results,args.draw)
		for i,draw in enumerate(list_of_draws):
			print("  {} - {}".format(dates[i],draw.strip()))
