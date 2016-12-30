import urllib2
import re
import nltk
import csv
import time
import requests
import string
from bs4 import BeautifulSoup
from urllib2 import urlopen
import os
import datetime
from firebase import firebase
import random
import os
import time
import sys
import urllib2
import re
import nltk
import time
import requests
import string
import webbrowser
import car
from urlparse import urlparse
from twilio.rest.resources import Connection
from twilio.rest.resources.connection import PROXY_TYPE_HTTP
from twilio.rest import TwilioRestClient
import movie
#proxy for my python anywhere account to run this script, you don't need it
host, port = urlparse(os.environ["http_proxy"]).netloc.split(":")
Connection.set_proxy_info(
            host,
                int(port),
                    proxy_type=PROXY_TYPE_HTTP,
                    )

# Find these values at https://twilio.com/user/account
account_sid = "YOUR-ACCOUNT-SID"
auth_token = "YOUR-AUTH-TOKEN"
client = TwilioRestClient(account_sid, auth_token)

def sendMessage(mess):
	message = client.messages.create(to="YOUR-NUMBER", from_="YOUR-TWILIO-NUMBER",
                                     body="\n\n\t"+mess)

"""
Following code runs everyday thanks to pythonanywhere.com
it determines which day it is and texts respective information
"""
if int(datetime.datetime.today().weekday()) == 0:
	movie.sendMessage("Movies Coming Out This Week")
	movie.sendMessage(getWeekMovies())
arr = getTodayMovies()
movie.sendMessage("Movies Coming Today")
for i in arr:
	moviesendMessage(getInfo(i))






