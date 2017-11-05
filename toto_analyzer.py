#!/usr/bin/env pythonw

#########################
# TOTO Analyzer         #
# Goh Khee Teck		#
# pydot4 class		#
#########################

import requests
import time
import subprocess
import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from wordcloud import WordCloud
from datetime import datetime

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
	"""Uses BeautifulSoup module to get the page source of a site

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
	"""Uses BeautifulSoup module to get the winning numbers from page source of a site

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

def generate_num_cloud(dict_of_num_freq):
	"""Plot the frequency of each winning number using WordCloud

        Args:
                dict_of_num_freq: a dict that contains each winning numbers frequency
        Returns:
                a numbercloud plot of the winning number occurance
        """
	numcloud = WordCloud().generate_from_frequencies(frequencies=dict_of_num_freq)
	plt.imshow(numcloud, interpolation ='bilinear')
	plt.axis("off")
	plt.show()

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

if __name__ == "__main__":
	url = "http://www.singaporepools.com.sg/en/product/Pages/toto_results.aspx"
	# read first from cache, if cache does not have, fetch from internet
	retrieve_updates_from_internet = False
	parser = argparse.ArgumentParser(description="TOTO analyzer for Singapore Pool v1.0")

	parser.add_argument("--plotfreq",
				help="plot number frequency using word cloud",
				action="store_true")

	parser.add_argument("--update",
				help="update local cache with latest records from Singapore Pool",
				action="store_true")

	parser.add_argument("-d", "--draw", type=int,
                    help="return list of last draws based on user input")

	parser.add_argument("-s", "--set", type=int,
                    help="return sets of random numbers, use together with -qp option")

	parser.add_argument("-qp", "--quickpick", type=int,
                    help="generate a list of random numbers")

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

	if args.quickpick is not None:
		random_list = []
		unique_list = []
		if args.draw is not None:
			dates,list_of_draws = get_last_drawn_num_rows(dict_of_results,args.draw)
			list_of_num = merge_list_rows_into_list_of_num(list_of_draws)
			unique_list = list(set(list_of_num))
		else:
			unique_list = range(1,50)

		print ("Your quick pick numbers are")
		if args.set is not None:
			random_list = generate_quickpick_list(unique_list,args.quickpick,args.set)
			for row in random_list:
                                print (row)
		else:
			random_list = generate_quickpick(unique_list,args.quickpick)
			print (random_list)

	if (args.draw is not None) & (args.quickpick is None):
		dates,list_of_draws = get_last_drawn_num_rows(dict_of_results,args.draw)
		for i,draw in enumerate(list_of_draws):
			print("  {} - {}".format(dates[i],draw.strip()))

