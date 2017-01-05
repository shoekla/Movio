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

globalData = []
globalMovies = []
globalPredictions = []
globalCast = []

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
		arr = eval(already[begin:end].replace('"','').replace("\"",""))
		return arr
	except Exception as e:
		print str(e)
		print "Error Single"
		return []
def getDataFromFireBase(name1,name2):
	already = str(db.child(name1).child(name2).get().val())
	#print already+"\n\n"
	arr = []
	try:
		begin = already.find(', u"')+4 #gets retrieved files
		if begin == 3:
			begin = already.find(", u'")+4
		#print begin
		end = -4
		arr = eval(already[begin:end].replace('"','').replace("\"",""))
		return arr
	except Exception as e:
		print str(e)
		print "Error Multiple"
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
	url = "http://rss.imdb.com/find?ref_=nv_sr_fn&q="+name+"&s=all"
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
			arr.append(title.replace("'","\'"))


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
def getInfoForMLSingle(name):
	url = getImdbLink(name)
	source_code=requests.get(url)
	plain_text=source_code.text
	soup=BeautifulSoup(plain_text)
	return getInfoForMLviaLinkSingle(soup)
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
	global globalCast
	oldCastCopy = globalCast
	count = 0
	for i in newCast:
		if i not in oldCastCopy:
			#print i +" not in cast list, so added" 
			count = count + 1
			globalCast.append(i)
	global globalData

	newdata = []
	addList = []
	for n in range(count):
		addList.append(0)
	for i in globalData:
		#print i
		#print "----"
		newdata.append(i+addList)
		#print newdata[data.index(i)]
	#for i in newdata:
	#	print str(len(i))
	globalData = newdata
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
def getInfoForMLviaLinkSingle(soup):
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
	info.append(cast)
	#print "Fantasy" in gens
	return info
#print addCast(a)
def translateToML(name):
	results = []
	genres = ['Fantasy-Romance', 'Biography-Crime', 'Comedy', 'Crime', 'Thriller', 'Biography', 'Thriller', 'War', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Crime', 'Mystery', 'Sport', 'Action', 'Horror', 'Romance', 'Drama', 'Mystery', 'Romance', 'Biography', 'Comedy', 'Crime', 'History', 'Romance', 'Film-Noir', 'Musical', 'War', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Crime', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Biography', 'Drama', 'War', 'Comedy', 'Drama', 'Sci-Fi', 'Biography', 'Documentary', 'Drama', 'Comedy', 'History', 'Romance', 'Adventure', 'Comedy', 'Thriller', 'Comedy', 'Crime', 'History', 'Thriller', 'Animation', 'Comedy', 'Family', 'Horror', 'Biography', 'Comedy', 'Documentary', 'Comedy', 'Crime', 'Horror', 'Mystery', 'Action', 'Biography', 'Comedy', 'Documentary', 'Action', 'Adventure', 'Comedy', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sitcom', 'Sport', 'Thriller', 'War', 'Western', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western', 'Anime']
	movieInfo = getInfoForML(name)
	global globalCast

	results.append(movieInfo[0])
	results.append(movieInfo[1])
	for i in genres:
		results.append(int(i in movieInfo[2]))
	#print str(count)+", "+str(len(results))
	results.append(movieInfo[3])
	for i in globalCast:
		results.append(int(i in movieInfo[4]))
	return results
def translateToMLSingle(name):
	results = []
	genres = ['Fantasy-Romance', 'Biography-Crime', 'Comedy', 'Crime', 'Thriller', 'Biography', 'Thriller', 'War', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Crime', 'Mystery', 'Sport', 'Action', 'Horror', 'Romance', 'Drama', 'Mystery', 'Romance', 'Biography', 'Comedy', 'Crime', 'History', 'Romance', 'Film-Noir', 'Musical', 'War', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Crime', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Biography', 'Drama', 'War', 'Comedy', 'Drama', 'Sci-Fi', 'Biography', 'Documentary', 'Drama', 'Comedy', 'History', 'Romance', 'Adventure', 'Comedy', 'Thriller', 'Comedy', 'Crime', 'History', 'Thriller', 'Animation', 'Comedy', 'Family', 'Horror', 'Biography', 'Comedy', 'Documentary', 'Comedy', 'Crime', 'Horror', 'Mystery', 'Action', 'Biography', 'Comedy', 'Documentary', 'Action', 'Adventure', 'Comedy', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sitcom', 'Sport', 'Thriller', 'War', 'Western', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western', 'Anime']
	movieInfo = getInfoForMLSingle(name)
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
	global globalPredictions
	global globalMovies
	global globalData
	global globalCast
	name = name.replace("'","\'")
	globalMovies = getDataFromFireBase("Movies")
	print "Got Movies"
	globalPredictions = getDataFromFireBase("Predictions")
	print "Predictions..."
	globalData = getDataFromFireBase("Data")
	print "Data..."
	globalCast = getDataFromFireBase("Cast")
	print "Cast...."
	#print globalCast
	if name in globalMovies:
		globalPredictions[globalMovies.index(name)] = like
		db.child("Predictions").remove()
		db.child("Predictions").push(str(globalPredictions))
		print name+" single updated"
		return
	arr = [name] + getRelatedMovies(name)
	for i in range(0,len(arr)):
		if arr[i] in globalMovies:
			globalPredictions[i] = like
			print arr[i]+" Updated"
		else:
			addToData = translateToML(arr[i])
			globalData.append(addToData)
			globalMovies.append(arr[i])
			globalPredictions.append(like)
			print arr[i]+" Learned"
		#print globalCast
	print "Done!"
	db.child("Data").remove()
	db.child("Data").push(str(globalData))
	db.child("Movies").remove()
	db.child("Movies").push(str(globalMovies))
	db.child("Predictions").remove()
	db.child("Predictions").push(str(globalPredictions))
	db.child("Cast").remove()
	#print globalCast
	#print "---------------g"
	db.child("Cast").push(str(globalCast).replace("\"",""))


def getMyMovies():
	res = []
	movies = getDataFromFireBase("Movies")
	pres = getDataFromFireBase("Predictions")
	for i in movies:
		res.append(i+": "+str(pres[movies.index(i)]))
	return res
def predictMovieML(name):
	info = translateToMLSingle(name)
	features = getDataFromFireBase("Data")
	labels = getDataFromFireBase("Predictions")
	if predict.predictMovieKNN(info,features,labels)[0] == 1:
		return "Yes you will like "+name
	return "No you will not like "+name
#name = "17 again: 0 ".strip()
#print name.endswith(": 0")
#startTime=time.time()
#db.child("Abir").child("Movies").push("Inception, Star Wars")

"""
db.child("Movies").push("[]")

addToML("Iron Man",1)
addToML("Star Wars",1)
addToML("Inception",1)
#cast =  getDataFromFireBase("Movies")
#print cast
addToML("The Notebook",0)
addToML("High School Musical",0)
addToML("Fifty Shades of grey",0)
"""
#timeA = time.time() - startTime
#print "Total Time: "+str(timeA)
#info = translateToML("Star Wars")
#print "-------------------------"
#features = getDataFromFireBase("Data")
#print "Info: "+str(len(info))
#genres = ['Fantasy-Romance', 'Biography-Crime', 'Comedy', 'Crime', 'Thriller', 'Biography', 'Thriller', 'War', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Crime', 'Mystery', 'Sport', 'Action', 'Horror', 'Romance', 'Drama', 'Mystery', 'Romance', 'Biography', 'Comedy', 'Crime', 'History', 'Romance', 'Film-Noir', 'Musical', 'War', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Crime', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Biography', 'Drama', 'War', 'Comedy', 'Drama', 'Sci-Fi', 'Biography', 'Documentary', 'Drama', 'Comedy', 'History', 'Romance', 'Adventure', 'Comedy', 'Thriller', 'Comedy', 'Crime', 'History', 'Thriller', 'Animation', 'Comedy', 'Family', 'Horror', 'Biography', 'Comedy', 'Documentary', 'Comedy', 'Crime', 'Horror', 'Mystery', 'Action', 'Biography', 'Comedy', 'Documentary', 'Action', 'Adventure', 'Comedy', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sitcom', 'Sport', 'Thriller', 'War', 'Western', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western', 'Anime']
#movies = getDataFromFireBase("Movies")
#print movies
#for i in features:
#	print movies[features.index(i)]+": "+str(len(i))
#print "Actual Len: "+str(3+len(genres)+len(getDataFromFireBase("Cast")))

#print str(len(info))
#print "-----------------------"
"""
info = translateToMLSingle("Devil Wears Prada")
features = getDataFromFireBase("Data")
labels = getDataFromFireBase("Predictions")
startTime=time.time()
print predict.predictMovie(info,features,labels)
"""
"""
timeA = time.time() - startTime
print "Total Time: "+str(timeA)
startTime=time.time()
print predict.predictMovieKNN(info,features,labels)
timeA = time.time() - startTime
print "Total Time KNN: "+str(timeA)


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














