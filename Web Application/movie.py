import urllib2
import re
import time
import requests
import string
from bs4 import BeautifulSoup
from urllib2 import urlopen
import os
import datetime
import pyrebase
import os





def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True
def getTitleOfMovie(td):
	begin = td.find("title=")
	res = td[begin+7:td.find('"',begin+7)]
	return res,begin+7
def getRatingUp(td,index):
	begin = td.find("title=",index)
	res = td[begin+7:td.find('"',begin+7)]
	if "ass" in res:
		return "Not Rated"
	return res
def getDuration(td):
	begin = td.find("duration")
	res = td[begin+10:td.find("m",begin)]
	return res
def getGenre(td):
	begin = td.find('"genre')
	res = td[begin+8:td.find("<",begin)]
	return res
def getMeta(td):
	begin = td.find('metascore')
	if begin == -1:
		return "NA"
	res = td[begin+23:td.find("<",begin)].strip()
	if len(res) == 0:
		return "NA"
	return res
def getDirector(td,index):
	begin = td.find('itemprop="url"',index)
	res = td[begin+15:td.find("<",begin)]
	if isEnglish(res):
		return res
	return "NA"
def getSumm(td):
	begin = td.find('itemprop="description"')
	res = td[begin+23:td.find("<",begin)]
	return res.strip()
def getLinkIM(td):
	res = td[55:td.find('"',55)]
	return res
def getRating(url):
	try:
		arr=[]
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('div', class_="ratingValue"):
			return removeHtml(str(link))


	except:
		print "Error at: "+str(url)
def getDataForMovie(url):
	pass
def getWeekMoviesList():
	try:
		url = "http://www.imdb.com/movies-in-theaters/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=2750721702&pf_rd_r=1AG21T14QV080Z1PT0AK&pf_rd_s=right-2&pf_rd_t=15061&pf_rd_i=homepage&ref_=hm_otw_sm"
		res = []
		source_code=requests.get(url)
		plain_text=source_code.text
		plain_text = plain_text[:plain_text.find("In Theaters Now")+1]
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('td',{ "class" : "overview-top" }):
			#print link
			td = str(link)
			
			imLink = getLinkIM(td)
			title, index = getTitleOfMovie(td)
			title = title.replace("'","")
			arr = [title,getRatingUp(td,index),getDuration(td),getGenre(td),getMeta(td),getDirector(td,index),getSumm(td),imLink]
			res.append(arr)
		return res
	except Exception as e: 
		print(e)
		return []

def getGoogLink(name):
	name = name.replace(" ","+")
	return "https://www.google.com/search?q="+name+"&oq=baby+driver&aqs=chrome..69i57j69i60.2214j0j9&sourceid=chrome&ie=UTF-8"
def turnToSearch(name):
	name = name.strip()
	name = name.replace(" ","%20")
	url = "http://www.imdb.com/find?q="+name+"&s=tt&ref_=fn_al_tt_mr"
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
def extractDataFromSearchResult(s):
	begin = s.find("<a")
	name = s[s.find(">",begin)+1:s.find("<",begin+1)]
	name = name.replace("'","")
	begin = s.find("a>")
	data = s[begin+2:s.find("<",begin)]
	begin = s.find("href")+6
	link = s[begin:s.find('"',begin)]
	if isEnglish(name):
		return [name,data,link]

def deleteDuplicates(lis):
	newLis=[]
	for item in lis:
		if item not in newLis:
			newLis.append(item)
	return newLis
def getMoviesSearch(name):
	try:
		url = turnToSearch(name)
		arr=[]
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('td', class_="result_text"):
			s = str(link)
			if "(TV" not in s and "(Video Game)" not in s and "(Production)" not in s and "(Post" not in s:
				if "title)" not in s and "titles)" not in s:
					extract = extractDataFromSearchResult(s)
					if extract != None:
						arr.append(extract)
		return arr

	except:
		#print "Error at: "+str(url)
		return []
def sumUP(arr):
	sumA = 0
	for i in arr:
		try:
			sumA = sumA + int(i)
		except:
			pass
	return sumA
#uses youtube to get movie trailer
def getTrailer(movie):
	movie = movie.replace(" ","+")
	movie = movie +"+trailer"
	link = "https://www.youtube.com/results?search_query="+movie
	return getVideoSearch(link)
def crawlYouTube(url):
	try:
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('a'):

			href_test=str(link.get('href'))
			if "/watch" in href_test:
				if href_test.startswith("http"):
						return href_test
				else:
					lin=getGoodLink(url)
					return lin+href_test

	except:
		print "Error at: "+str(url)
def getGoodLink(url):
	k = url.rfind("/")
	return url[:k ]
def getVideoSearch(url):
	item = crawlYouTube(url)
	if "/watch" in item:
		return item[item.find("v=")+2:]
def getInfoForMovieML(link):
	source_code=requests.get(link)
	plain_text=source_code.text
	soup=BeautifulSoup(plain_text)
	return getInfoForMLviaLink(soup)
def getInfoForMLviaLink(soup):
	info = []
	rating = 7
	for link in soup.findAll('div', class_="ratingValue"):
			rating = float(removeHtml(str(link))[:-3])
			break
	metaRating = int(rating*10)
	for link in soup.findAll('div', class_="metacriticScore score_favorable titleReviewBarSubItem"):
			metaRating = float(removeHtml(str(link)))
	info.append(rating)
	info.append(metaRating)
	gen = []
	for link in soup.findAll('div', class_="see-more inline canwrap"):
			gen = removeHtml(str(link)).replace("\xc2\xa0","").replace("\n","").replace("Genres:","").split("|")
	gens = []
	for i in gen:
		gens.append(i.strip())
	##print gens
	info.append(gens)
	awards = 0
	for link in soup.findAll('span', itemprop="awards"):
		awards = awards + sumUP(removeHtml(str(link)).replace("\n","").split(" "))
	##print awards
	info.append(awards)
	lengthMovie = 0
	for link in soup.findAll('time',itemprop="duration"):
		t=removeHtml(link)
		lengthMovie = t[:t.find("m")]
	info.append(int(lengthMovie))
	##print info
	cast = []
	for link in soup.findAll('span', itemtype="http://schema.org/Person"):
		c = removeHtml(str(link)).replace(",","")
		if isEnglish(c):
			cast.append(c)
	cast = deleteDuplicates(cast)
	info.append(cast)
	summary = "No summary available"
	for link in soup.findAll('div', class_="summary_text"):
		summary = removeHtml(link)
	recs = []
	for link in soup.findAll('div', class_="rec-title"):
		s = str(link)
		a = []
		begin = s.find("href")+6
		end = s.find('"',begin)
		href = s[begin:end]
		#print href
		begin = end
		title = s[begin+5:s.find("</b>")]
		if isEnglish(title):
			#print title
			a.append(title)
			begin = s.find('nobr">',begin)+6
			data = s[begin:s.find("<",begin)]
			#print data
			a.append(data)
			a.append(href)
			recs.append(a)
	##print "Fantasy" in gens
	return info,summary,recs




def getInfoForMovieMLUp(link):
	source_code=requests.get(link)
	plain_text=source_code.text
	soup=BeautifulSoup(plain_text)
	return getInfoForMLviaLinkUp(soup)
def getInfoForMLviaLinkUp(soup):
	info = []
	rating = 7
	for link in soup.findAll('div', class_="ratingValue"):
			rating = float(removeHtml(str(link))[:-3])
			break
	metaRating = int(rating*10)
	for link in soup.findAll('div', class_="metacriticScore score_favorable titleReviewBarSubItem"):
			metaRating = float(removeHtml(str(link)))
	info.append(rating)
	info.append(metaRating)
	gen = []
	for link in soup.findAll('div', class_="see-more inline canwrap"):
			gen = removeHtml(str(link)).replace("\xc2\xa0","").replace("\n","").replace("Genres:","").split("|")
	gens = []
	for i in gen:
		gens.append(i.strip())
	##print gens
	info.append(gens)
	awards = 0
	for link in soup.findAll('span', itemprop="awards"):
		awards = awards + sumUP(removeHtml(str(link)).replace("\n","").split(" "))
	##print awards
	info.append(awards)
	lengthMovie = 0
	for link in soup.findAll('time',itemprop="duration"):
		t=removeHtml(link)
		lengthMovie = t[:t.find("m")]
	info.append(int(lengthMovie))
	##print info
	cast = []
	for link in soup.findAll('span', itemtype="http://schema.org/Person"):
		c = removeHtml(str(link)).replace(",","")
		if isEnglish(c):
			cast.append(c)
	cast = deleteDuplicates(cast)
	info.append(cast)
	recs = []
	for link in soup.findAll('div', class_="rec-title"):
		s = str(link)
		a = []
		begin = s.find("href")+6
		end = s.find('"',begin)
		href = s[begin:end]
		#print href
		begin = end
		title = s[begin+5:s.find("</b>")]
		if isEnglish(title):
			#print title
			a.append(title)
			begin = s.find('nobr">',begin)+6
			data = s[begin:s.find("<",begin)]
			#print data
			a.append(data)
			a.append(href)
			recs.append(a)

	
	##print "Fantasy" in gens
	return info,recs

"""
#test for movie data
url = "http://www.imdb.com/title/tt0491203/?ref_=inth_ov_tt"

print getInfoForMovieML(url)

#test for getMovie Search
a = getMoviesSearch("Kill Bill")
for i in a:
	print i

#test for Get Movie Week List
a = getWeekMoviesList()

for i in a:
	print len(i)

"""


