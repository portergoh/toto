#!/usr/bin/env pythonw

#################################
# TOTO Analyzer using Alexa 	#
# Goh Khee Teck			#
# pydot4 class			#
#################################

from toto_analyzer import get_past_results,get_last_drawn_num_rows
from flask import Flask
from flask_ask import Ask,statement,question

app = Flask(__name__)
ask = Ask(app, "/toto_analyzer")

@app.route("/")
def hompage():
	return 	"""
		This is a tool developed as part of the 'Python for Data, Ops and Things' course.\n
		It collect and analyse data from Singapore pool.
		"""
@ask.launch
def start_skill():
	welcome_message = "Hello kheeteck, do you like to know the latest toto results ?"
	return question(welcome_message)

@ask.intent("YesIntent")
def get_last_draw():
	url = "http://www.singaporepools.com.sg/en/product/Pages/toto_results.aspx"
	dict_of_results = get_past_results(url,False)
	_,list_of_draws = get_last_drawn_num_rows(dict_of_results,1)
	draw_result = "The result is " + " ".join(num for num in list_of_draws)

	return statement(draw_result)

@ask.intent("NoIntent")
def no_intent():
	bye_text = "I am not sure why you ask me to run then, but okie goodbye"
	return statement(bye_text)

if __name__ == "__main__":
	app.run(debug=True)
