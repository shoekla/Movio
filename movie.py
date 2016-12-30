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


#gets today date for movie matching
def getDate():
	today = datetime.date.today()
	s = str(today).replace("-","/")
	return s[5:]
#turns query to imdb search url
def turnToSearch(name):
	name = name.strip()
	name = name.replace(" ","+")
	url = "http://www.imdb.com/find?ref_=nv_sr_fn&q="+name+"&s=all"
	return url
#removes html tags from given string
def removeHtml(s):
	res = ""
	check = True
	for i in s:
		if check:
			if i == "<":
				check = False
			else:
				res = res+i
		else:
			if i ==">":
				check = True
	return res.strip()
#gets movie name from imdb, Ex: A new hope -> Star Wars: Episode IV - A New Hope (1977)
def getMovie(name):
	try:
		url = turnToSearch(name)
		arr=[]
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('td', class_="result_text"):
			s = str(link)
			if "(TV Episode)" not in s:
				return removeHtml(s)


	except:
		print "Error at: "+str(url)
#gets imdb link of actual movie
def getImdbLink(name):
	try:
		url = turnToSearch(name)
		arr=[]
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('td', class_="result_text"):
			s = str(link)
			if "(TV Episode)" not in s:
				begin = s.find("href=")
				if begin == -1:
					return
				end = s.find(">",begin)

				return "http://www.imdb.com"+s[begin+6:end-1]


	except:
		print "Error at: "+str(url)
#gets movie rating from imdb
def getRating(name):
	try:
		url = getImdbLink(name)
		arr=[]
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('div', class_="ratingValue"):
			return "Rating: "+removeHtml(str(link))+"\n"+"IMDB Link: "+url


	except:
		print "Error at: "+str(url)
#uses youtube to get movie trailer
def getTrailer(movie):
	movie = movie.replace(" ","+")
	movie = movie +"+trailer"
	link = "https://www.youtube.com/results?search_query="+movie
	return getVideoSearch(link)
def crawlYouTube(url,pages):
	try:
		arr=[]
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('a'):

			href=link.get('href')
			href_test=str(href)
			if href_test.startswith("http"):
					pages.append(str(href))
			else:
				lin=getGoodLink(url)
				pages.append(lin+str(href))

	except:
		print "Error at: "+str(url)
def getVideoSearch(url):
	a = []
	crawlYouTube(url,a)
	b=[]
	c=[]
	for item in a:
		if "/watch" in item:
			return str(item)
def getGoodLink(url):
	k = url.rfind("/")
	return url[:k ]
#puts all information into one, for the text message
def getInfo(name):
	name = getMovie(name)
	res = name+"\n"+"Trailer: "+getTrailer(name)+"\n"+ getRating(name)
	return res
#returns a string containing all movies coming out in the current week
def getWeekMovies():
	try:
		url = "http://rss.imdb.com/movies-in-theaters/?ref_=cs_inth"
		res = ""
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('h4', itemprop="name"):
			s = removeHtml(str(link))
			if "- [" not in s:
				return res
			res = res+"\n"+s
		return res
	except:
		return ""
#returns a list of all movies coming out on the current day
def getTodayMovies():
	try:
		url = "http://rss.imdb.com/movies-in-theaters/?ref_=cs_inth"
		arr = []
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		date = getDate()
		for link in soup.findAll('h4', itemprop="name"):
			s = removeHtml(str(link))
			if "- [" not in s:
				return arr
			if date in s:
				arr.append(s[:s.find("- [")-8])
		return arr
	except:
		return []

















