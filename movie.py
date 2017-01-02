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
import pyrebase
import os
import predict
config = {
  "apiKey": "AIzaSyBWNvx1_eEJNzvesTfP6OdlwYluv7ar0Qs",
  "authDomain": "movio-96dae.firebaseapp.com",
  "databaseURL": "https://movio-96dae.firebaseio.com/",
  "storageBucket": "movio-96dae.appspot.com"
}


firebase = pyrebase.initialize_app(config)
db = firebase.database()
"""
Push this first to get app started for the first time
db.child("Movies").push("[]")
db.child("Predictions").push("[]")
db.child("Data").push("[]")
db.child("Cast").push("[]")
"""
#Gets data from firebase via Key
def getDataFromFireBase(name):
	already = str(db.child(name).get().val())
	#print already+"\n\n"
	arr = []
	try:
		begin = already.find(', u"')+4 #gets retrieved files
		if begin == 3:
			begin = already.find(", u'")+4
		#print begin
		end = -4
		arr = eval(already[begin:end])
		return arr
	except:
		print "Error"
		return []

def deleteDuplicates(lis):
	newLis=[]
	for item in lis:
		if item not in newLis:
			newLis.append(item)
	return newLis

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
#returns list of search for movie
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
					arr.append(removeHtml(s))
		return arr

	except:
		print "Error at: "+str(url)
		return []

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

				return "http://rss.imdb.com"+s[begin+6:end-1]


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
genres = ['Fantasy-Romance', 'Biography-Crime', 'Comedy', 'Crime', 'Thriller', 'Biography', 'Thriller', 'War', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Crime', 'Mystery', 'Sport', 'Action', 'Horror', 'Romance', 'Drama', 'Mystery', 'Romance', 'Biography', 'Comedy', 'Crime', 'History', 'Romance', 'Film-Noir', 'Musical', 'War', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Crime', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Biography', 'Drama', 'War', 'Comedy', 'Drama', 'Sci-Fi', 'Biography', 'Documentary', 'Drama', 'Comedy', 'History', 'Romance', 'Adventure', 'Comedy', 'Thriller', 'Comedy', 'Crime', 'History', 'Thriller', 'Animation', 'Comedy', 'Family', 'Horror', 'Biography', 'Comedy', 'Documentary', 'Comedy', 'Crime', 'Horror', 'Mystery', 'Action', 'Biography', 'Comedy', 'Documentary', 'Action', 'Adventure', 'Comedy', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sitcom', 'Sport', 'Thriller', 'War', 'Western', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western', 'Anime']


def getRelatedMovies(name):
	url = getImdbLink(name)
	print url
	try:
		arr=[]
		source_code=requests.get(url)
		plain_text=source_code.text
		soup=BeautifulSoup(plain_text)
		for link in soup.findAll('img', height="113"):
			title = link.get('alt')
			#print str(title)
			arr.append(title)


		return arr
	except:
		print "Error at: "+str(url)
		return []

def getInfoForML(name):
	url = getImdbLink(name)
	source_code=requests.get(url)
	plain_text=source_code.text
	soup=BeautifulSoup(plain_text)
	return getInfoForMLviaLink(soup)
def sumUP(arr):
	sumA = 0
	for i in arr:
		try:
			sumA = sumA + int(i)
		except:
			pass
	return sumA
def addCast(newCast):
	newCast = deleteDuplicates(newCast)
	oldCast = getDataFromFireBase("Cast")
	oldCastCopy = getDataFromFireBase("Cast")
	count = 0
	for i in newCast:
		if i not in oldCastCopy:
			#print i +" not in cast list, so added" 
			count = count + 1
			oldCast.append(i)
	db.child("Cast").remove()
	db.child("Cast").push(str(oldCast))
	data = getDataFromFireBase("Data")
	newdata = []
	addList = []
	for n in range(count):
		addList.append(0)
	for i in data:
		#print i
		#print "----"
		newdata.append(i+addList)
		#print newdata[data.index(i)]
	#for i in newdata:
	#	print str(len(i))
	db.child("Data").remove()
	db.child("Data").push(str(newdata))
def getInfoForMLviaLink(soup):
	info = []
	rating = 7
	for link in soup.findAll('div', class_="ratingValue"):
			rating = float(removeHtml(str(link))[:-3])
			break
	metaRating = 75
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
	#print gens
	info.append(gens)
	awards = 0
	for link in soup.findAll('span', itemprop="awards"):
		awards = awards + sumUP(removeHtml(str(link)).replace("\n","").split(" "))
	#print awards
	info.append(awards)
	#print info
	cast = []
	for link in soup.findAll('span', itemtype="http://schema.org/Person"):
		cast.append(removeHtml(str(link)).replace(",",""))
	addCast(cast)
	info.append(cast)
	#print "Fantasy" in gens
	return info

#print addCast(a)
def translateToML(name):
	results = []
	genres = ['Fantasy-Romance', 'Biography-Crime', 'Comedy', 'Crime', 'Thriller', 'Biography', 'Thriller', 'War', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Crime', 'Mystery', 'Sport', 'Action', 'Horror', 'Romance', 'Drama', 'Mystery', 'Romance', 'Biography', 'Comedy', 'Crime', 'History', 'Romance', 'Film-Noir', 'Musical', 'War', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Crime', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Biography', 'Drama', 'War', 'Comedy', 'Drama', 'Sci-Fi', 'Biography', 'Documentary', 'Drama', 'Comedy', 'History', 'Romance', 'Adventure', 'Comedy', 'Thriller', 'Comedy', 'Crime', 'History', 'Thriller', 'Animation', 'Comedy', 'Family', 'Horror', 'Biography', 'Comedy', 'Documentary', 'Comedy', 'Crime', 'Horror', 'Mystery', 'Action', 'Biography', 'Comedy', 'Documentary', 'Action', 'Adventure', 'Comedy', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sitcom', 'Sport', 'Thriller', 'War', 'Western', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western', 'Anime']
	movieInfo = getInfoForML(name)
	cast = getDataFromFireBase("Cast")
	results.append(movieInfo[0])
	results.append(movieInfo[1])
	for i in genres:
		results.append(int(i in movieInfo[2]))
	#print str(count)+", "+str(len(results))
	results.append(movieInfo[3])
	for i in cast:
		results.append(int(i in movieInfo[4]))
	return results
#print translateToML("A New Hope")



def addToML(name,like):
	arr = [name] + getRelatedMovies(name)
	movies = getDataFromFireBase("Movies")
	predictions = getDataFromFireBase("Predictions")
	data = getDataFromFireBase("Data")
	for i in range(0,len(arr)):
		if arr[i] in movies:
			predictions[i] = like
			print arr[i]+" Updated"
		else:
			addToData = translateToML(arr[i])
			data = getDataFromFireBase("Data")
			data.append(addToData)
			movies.append(arr[i])
			predictions.append(like)
			print arr[i]+" Learned"
		db.child("Data").remove()
		db.child("Data").push(str(data))
	print "Done!"
	db.child("Data").remove()
	db.child("Data").push(str(data))
	db.child("Movies").remove()
	db.child("Movies").push(str(movies))
	db.child("Predictions").remove()
	db.child("Predictions").push(str(predictions))
def updatePredictions():
	length = 3+len(genres)+len(getDataFromFireBase("Cast"))
	features = getDataFromFireBase("Data")
	old = length - len(features[0])
	newArr = []
	for n in range(old):
		newArr.append(0)
	newFeatures = []
	for i in features:
		arr = i+newArr
		newFeatures.append(arr)
	db.child("Data").remove()
	db.child("Data").push(str(newFeatures))


startTime=time.time()

addToML("Twilight",0)
#timeA = time.time() - startTime
#print "Total Time: "+str(timeA)

info = translateToML("Twilight")
print "-----------------------"
print str(len(info))
features = getDataFromFireBase("Data")
for i in features:
	print str(len(i))

print "Actual Len: "+str(3+len(genres)+len(getDataFromFireBase("Cast")))


"""
old = getDataFromFireBase("Data")
for i in old:
	print i

print "--------------------"
ca = ['Abir','Aadi','Chini']
addCast(ca)
newD = getDataFromFireBase("Data")
for i in newD:
	print i
print "------------"
ca = ['Abir','Aadi','Chini',"Varsha","Ajay"]
addCast(ca)
newD = getDataFromFireBase("Data")
for i in newD:
	print i

"""

