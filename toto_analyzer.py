#!/usr/bin/env pythonw

#########################
# TOTO Analyzer         #
# Goh Khee Teck		#
# pydot4 class		#
#########################

import requests
import time
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from wordcloud import WordCloud
from datetime import datetime
from collections import OrderedDict

SLEEP_TIME = 1

def is_record_exist(date, file_path):
	"""Uses grep to search for a date record

    	Args:
        	date: string object to search for
		file_path: absolute path to the location of the file
    	Returns:
        	True or False
	"""
        cmd = "grep -w '{}' {}".format(date,file_path)
        try:
                output = subprocess.check_output(cmd,shell=True)
                if output:
                        return True
        except:
                return False

def write_record_to_cache(record,file_path):
	"""Append a date record to a file

        Args:
                record: contains a string object which has the date and toto numbers
                file_path: absolute path to the location of the file
        """
	cmd = "echo {} >> {}".format(record,file_path)
	output = subprocess.check_output(cmd,shell=True)

def get_page_source(url):
	"""Uses selenium module to get the page source of a site

        Args:
                url: web address of a site
        Returns:
               	a selenium object of the page source
        """
	driver = webdriver.Firefox()
        driver.get(url)
        page_source = driver.page_source.encode('utf-8')
	return page_source

def get_result_content(url):
	"""Uses BeautifulSoup module to get the page source from Singapore Pool result detail page

        Args:
                url: web address of a site
        Returns:
                soup object of the page
        """
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	page_source = requests.get(url,headers=headers).content
	#page_source = get_page_source(url)
	result_detail = BeautifulSoup(page_source,"html.parser")
	return result_detail

def get_winning_numbers(page_detail):
	"""Uses BeautifulSoup module to get the winning numbers from page source of Singapore Pool result detail page

        Args:
                page_detail: soup object
        Returns:
               	a list of winning numbers
        """
	winning_numbers = []
	for i in range(1,7):
		win_tag = page_detail.find("td", {"class":"win{}".format(i)})
		if win_tag:
			winning_numbers.append(win_tag.get_text().encode("utf8"))
	return winning_numbers

def get_past_results(url,update_from_sgpool=False):
	"""Retrieve past TOTO records from cache

        Args:
                url: web address of Singapore pool site
		update_from_sgpool: default is set to False, setting it True will fetch new updates
				    from Singapore pool
        Returns:
                a dict of past records of winning numbers
        """
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
	"""Read from file and return a dict object of the data

        Args:
                path: absolute path to the location of the file
        Returns:
                a dict representation of the file records
        """
	dict_of_results = {}
	with open(path, "r") as fint:
		for line in fint:
			split_str = line.split(",")
			date = split_str[0] + "," + split_str[1]
			dict_of_results[date] = split_str[2]
	return  dict_of_results

def merge_list_rows_into_list_of_num(num_row_list):
	""" Merge all the sublists into a single list

        Args:
                num_row_list: a list that contains many sublist of winning numbers
        Returns:
                a list of winning numbers
        """
        list_of_num = []
        for num_row in num_row_list:
                num_row_split = num_row.split()
                for num in num_row_split:
                        list_of_num.append(num)
        return list_of_num

def compute_num_frequency(num_row_list):
	"""Compute the frequency of each number in a list

        Args:
                num_row_list: a list that contains many sublist of winning numbers
        Returns:
                a dict of winning numbers which has the value of the occurance frequency
        """
	dict_of_num_freq = {}

	list_of_num = merge_list_rows_into_list_of_num(num_row_list)

	for num in list_of_num:
		if num in dict_of_num_freq:
			dict_of_num_freq[num] += 1
		else:
			dict_of_num_freq[num] = 1

	#for k,v in dict_of_num_freq.items():
	#	print ("{} - {}".format(k,v))

	return dict_of_num_freq

def get_last_drawn_num_rows(dict_of_results,num):
	"""Obtain winning numbers based on x number of last draw

        Args:
                dict_of_results: a dict representation of all winning records
		num: number which indicate how many draws
        Returns:
                a tuple that contains a list of last drawn dates and winning records
        """
	selected_num_rows = []
	sorted_keys = sorted(dict_of_results.iterkeys(),key=lambda x: datetime.strptime(x, "%a, %d %b %Y"),reverse=True)
	for key in sorted_keys[0:num]:
		selected_num_rows.append(dict_of_results[key])
	return sorted_keys,selected_num_rows


def plot_num_freq_using_word_cloud(list_of_draws):
	"""Plot the frequency of each winning number using WordCloud

        Args:
		list_of_draws: a list of row of numbers of past draws
        Returns:
                a numbercloud plot of the winning number occurance
        """
 	dict_of_num_freq = compute_num_frequency(list_of_draws)
	numcloud = WordCloud().generate_from_frequencies(frequencies=dict_of_num_freq)
	plt.imshow(numcloud, interpolation ='bilinear')
	plt.axis("off")
	plt.show()

def plot_num_freq_using_bar(list_of_draws):
	"""Plot using bar chart to show the number frequency

        Args:
                list_of_draws: a list of row of numbers of past draws
        """
	dict_num_freq = compute_num_frequency(list_of_draws)
	sorted_num_keys = sorted(dict_num_freq.keys(), key = lambda x: int(x))
	sorted_dict_num_freq = OrderedDict()
	for key in sorted_num_keys:
		sorted_dict_num_freq[key] = dict_num_freq[key]

	#keys become rows
	df = pd.DataFrame.from_dict(sorted_dict_num_freq, orient="index")
	df.columns = ["frequency"]
	ax = df.plot(kind="bar",title ="Toto number frequency", figsize=(12, 8), legend=False, fontsize=11)
	ax.set_xlabel("TOTO numbers", fontsize=12)
	ax.set_ylabel("Frequency", fontsize=12)
	plt.show()

def generate_quickpick(num_list,num):
	"""Generate random winning numbers based on a defined list

        Args:
                num_list: a list of numbers
                num: indicate how many numbers to generate
        Returns:
                a list of random numbers size defined by user
        """
	random_list  = np.random.choice(num_list,num,replace=False)
	return random_list

def generate_quickpick_list(num_list,num,row):
	"""Generate sets of random winning numbers based on a defined list

        Args:
                num_list: a list of numbers
                num: indicate how many numbers to generate
		row: how many sets to generate
        Returns:
                a list of set of random numbers size defined by user
        """
	list_of_rows = []
	for _ in range(0,row):
		random_list = generate_quickpick(num_list,num)
		list_of_rows.append(random_list)
	return list_of_rows

def get_num_not_in_past_draw(past_draw_nums):
	"""Get numbers that is outside of past draws
        Args:
                past_draw_nums: a list of unique numbers for past draws
        Returns:
                a list of numbers that are not in past draws
        """
	num_not_in_past_draw = range(1,50)
	for num in past_draw_nums:
		num_int = int(num.strip())
		if num_int in num_not_in_past_draw:
			num_not_in_past_draw.remove(num_int)

	return	num_not_in_past_draw

if __name__ == "__main__":
	import argparse

	url = "http://www.singaporepools.com.sg/en/product/Pages/toto_results.aspx"
	# read first from cache, if cache does not have, fetch from internet
	retrieve_updates_from_internet = False
	parser = argparse.ArgumentParser(description="TOTO analyzer for Singapore Pool v1.0")

	parser.add_argument("--plotfreqwc",
				help="plot number frequency using word cloud",
				action="store_true")

	parser.add_argument("--plotfreqbc",
                         	help="plot number frequency using bar chart",
                         	action="store_true")

	parser.add_argument("--notin",
                                help="option to indicate not to select numbers from any of the selected draw",
                                action="store_true")

	parser.add_argument("--update",
				help="update local cache with latest records from Singapore Pool",
				action="store_true")

	parser.add_argument("-d", "--draw", type=int,
                    		help="return x number of last draws winning numbers")

	parser.add_argument("-s", "--set", type=int,
                    		help="return sets of random numbers, can be use together with -qp option")

	parser.add_argument("-qp", "--quickpick", type=int,
                    		help="generate a list of random numbers, can be use together with -d option")

	args = parser.parse_args()
        if args.update:
		retrieve_updates_from_internet = True

	dict_of_results = get_past_results(url,retrieve_updates_from_internet)

        if (args.plotfreqwc) & (args.draw is None):
		plot_num_freq_using_word_cloud(dict_of_results.values())

	if (args.plotfreqwc) & (args.draw is not None):
		_,list_of_draws = get_last_drawn_num_rows(dict_of_results,args.draw)
                plot_num_freq_using_word_cloud(list_of_draws)

	if (args.plotfreqbc) & (args.draw is None):
		plot_num_freq_using_bar(dict_of_results.values())

	if (args.plotfreqbc) & (args.draw is not None):
		_,list_of_draws = get_last_drawn_num_rows(dict_of_results,args.draw)
		plot_num_freq_using_bar(list_of_draws)

	if args.quickpick is not None:
		random_list = []
		input_list = []

		_,list_of_draws = get_last_drawn_num_rows(dict_of_results,args.draw)
                list_of_num = merge_list_rows_into_list_of_num(list_of_draws)
		past_draw_nums_list = list(set(list_of_num))

		if args.draw is None:
		 	input_list = range(1,50)
		elif (args.draw) & (args.notin is not True):
			input_list = past_draw_nums_list
		elif (args.draw) & (args.notin):
			input_list = get_num_not_in_past_draw(past_draw_nums_list)

		print ("Your quick pick numbers are")
		if args.set is not None:
			random_list = generate_quickpick_list(input_list,args.quickpick,args.set)
			for row in random_list:
                                print (row)
		else:
			random_list = generate_quickpick(input_list,args.quickpick)
			print (random_list)

	if (args.draw is not None) & (args.quickpick is None):
		dates,list_of_draws = get_last_drawn_num_rows(dict_of_results,args.draw)
		for i,draw in enumerate(list_of_draws):
			print("  {} - {}".format(dates[i],draw.strip()))

