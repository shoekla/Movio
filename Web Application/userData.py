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
  """Firebase Login"""
}



firebase = pyrebase.initialize_app(config)
db = firebase.database()
"""
Push this first to get app started for the first time
db.child("Movies").set("[]")
db.child("Predictions").set("[]")
db.child("Data").set("[]")
db.child("Cast").set("[]")
"""
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True
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
def sumUP(arr):
	sumA = 0
	for i in arr:
		try:
			sumA = sumA + int(i)
		except:
			pass
	return sumA

def deleteDuplicates(lis):
	newLis=[]
	for item in lis:
		if item not in newLis:
			newLis.append(item)
	return newLis
def turnToSearch(name):
	name = name.strip()
	name = name.replace(" ","+")
	url = "http://www.imdb.com/find?ref_=nv_sr_fn&q="+name+"&s=all"
	return url
def getMLFromName(name):
	return getInfoForMovieML(getImdbLink(name))
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
def getInfoForMovieML(link):
	source_code=requests.get(link)
	plain_text=source_code.text
	soup=BeautifulSoup(plain_text)
	return getInfoForMLviaLinkSignUp(soup)
def getInfoForMLviaLinkSignUp(soup):
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
	nameM = ""
	for link in soup.findAll('h1',itemprop="name"):
		nameM = removeHtml(str(link))
	nameM = nameM[:nameM.find(" (")]
	return info,nameM
#getMLFromName("Good Time")
#Gets data from firebase via Key
def getDataFromFireBase(name):
	s = db.child(name).get().val()
	if isinstance(s, basestring):
		return eval(s)
	return s
	
def getDataFromFireBaseMultiple(name1,name2):
	s = db.child(name1).child(name2).get().val()
	if isinstance(s, basestring):
		return eval(s)
	return s
	
def checkMovieRating(user,movieName):
	arr = getDataFromFireBaseMultiple(user,"Movies")
	arrP = getDataFromFireBaseMultiple(user,"Predictions")
	if movieName in arr:
		for i in range(len(arr)):
			if arr[i] == movieName:
				return arrP[i]
	return None
#print checkMovieRating("shoekla","Baby Driver")

genres = ['Fantasy-Romance', 'Biography-Crime', 'Comedy', 'Crime', 'Thriller', 'Biography', 'Thriller', 'War', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Crime', 'Mystery', 'Sport', 'Action', 'Horror', 'Romance', 'Drama', 'Mystery', 'Romance', 'Biography', 'Comedy', 'Crime', 'History', 'Romance', 'Film-Noir', 'Musical', 'War', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Crime', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Biography', 'Drama', 'War', 'Comedy', 'Drama', 'Sci-Fi', 'Biography', 'Documentary', 'Drama', 'Comedy', 'History', 'Romance', 'Adventure', 'Comedy', 'Thriller', 'Comedy', 'Crime', 'History', 'Thriller', 'Animation', 'Comedy', 'Family', 'Horror', 'Biography', 'Comedy', 'Documentary', 'Comedy', 'Crime', 'Horror', 'Mystery', 'Action', 'Biography', 'Comedy', 'Documentary', 'Action', 'Adventure', 'Comedy', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sitcom', 'Sport', 'Thriller', 'War', 'Western', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western', 'Anime']

def addCast(user,cast):
	print "Adding Cast.."
	#time.sleep(3)
	oldCast = getDataFromFireBaseMultiple(user,"Cast")
	res = deleteDuplicates(oldCast+cast)
	l = [0] * (len(res) - len(oldCast))
	#print "User: "+str(user)
	oldData = getDataFromFireBaseMultiple(user,"Data")
	#print "Old Data: "+str(oldData)
	#time.sleep(3)
	if oldData == None:
		return res,[]
	
	for i in range(len(oldData)):
		oldData[i] = oldData[i]+l

	db.child(user).child("Cast").set(res)
	#print "Old Data 2: "+str(oldData)
	return res, oldData
def translateToML(movieInfo,user):
	results = []
	genres = ['Fantasy-Romance', 'Biography-Crime', 'Comedy', 'Crime', 'Thriller', 'Biography', 'Thriller', 'War', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Crime', 'Mystery', 'Sport', 'Action', 'Horror', 'Romance', 'Drama', 'Mystery', 'Romance', 'Biography', 'Comedy', 'Crime', 'History', 'Romance', 'Film-Noir', 'Musical', 'War', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Crime', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Biography', 'Drama', 'War', 'Comedy', 'Drama', 'Sci-Fi', 'Biography', 'Documentary', 'Drama', 'Comedy', 'History', 'Romance', 'Adventure', 'Comedy', 'Thriller', 'Comedy', 'Crime', 'History', 'Thriller', 'Animation', 'Comedy', 'Family', 'Horror', 'Biography', 'Comedy', 'Documentary', 'Comedy', 'Crime', 'Horror', 'Mystery', 'Action', 'Biography', 'Comedy', 'Documentary', 'Action', 'Adventure', 'Comedy', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sitcom', 'Sport', 'Thriller', 'War', 'Western', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western', 'Anime']
	#movieInfo = getInfoForML(name,user)

	results.append(movieInfo[0])#imdb
	results.append(movieInfo[1])#meta
	#genres
	for i in genres:
		results.append(int(i in movieInfo[2]))
	##print str(count)+", "+str(len(results))
	results.append(movieInfo[3])#awards
	results.append(movieInfo[4])#length
	cast, oldData = addCast(user,movieInfo[5])
	#print "Old Data 3: "+str(oldData)
	for i in cast:
		try:
			results.append(int(i in movieInfo[5]))
		except:
			results.append(0)
	print cast
	oldData.append(results)
	#print "DataM: "+str(dataM)
	return oldData




def addToMLForUser(movieInfo,like,user,name):
	movies = getDataFromFireBaseMultiple(user,"Movies")
	predictions = getDataFromFireBaseMultiple(user,"Predictions")
	if name in movies:
		predictions[movies.index(name)] = like
		db.child(user).child("Predictions").set(predictions)
		return None
	dataMovie = translateToML(movieInfo,user)
	#print "Data Movie: "+str(dataMovie)
	db.child(user).child("Data").set(dataMovie)
	movies.append(name)
	db.child(user).child("Movies").set(movies)
	predictions.append(like)
	db.child(user).child("Predictions").set(predictions)

def addUser(name):
	print "Adding"
	db.child(name).child("Movies").set("[]")
	db.child(name).child("Cast").set("[]")
	db.child(name).child("Predictions").set("[]")
	db.child(name).child("Data").set("[]")
def addUserToFire(name,password,loveMovies,hateMovies):
	users = db.child("Users").get().val()
	if name in users:
		return False
	users = users+","+name
	passw = str(db.child("PassW").get().val())+","+password
	db.child("Users").set(users)
	db.child("PassW").set(passw)
	addUser(name)
	if len(loveMovies) > 0:
		lm = loveMovies.split(",")
		for i in lm:
			print "Movie: "+i
			movieInfo, movieName = getMLFromName(i)
			addToMLForUser(movieInfo,"Love",name,movieName)
	if len(hateMovies) > 0:
		hm = hateMovies.split(",")
		for i in hm:
			movieInfo, movieName = getMLFromName(i)
			addToMLForUser(movieInfo,"Hate",name,movieName)
	return True

def translateForPrediction(movieInfo,user):
	results = []
	genres = ['Fantasy-Romance', 'Biography-Crime', 'Comedy', 'Crime', 'Thriller', 'Biography', 'Thriller', 'War', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Crime', 'Mystery', 'Sport', 'Action', 'Horror', 'Romance', 'Drama', 'Mystery', 'Romance', 'Biography', 'Comedy', 'Crime', 'History', 'Romance', 'Film-Noir', 'Musical', 'War', 'Adventure', 'Comedy', 'Fantasy', 'Romance', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Crime', 'Mystery', 'Romance', 'Thriller', 'Adventure', 'Biography', 'Drama', 'War', 'Comedy', 'Drama', 'Sci-Fi', 'Biography', 'Documentary', 'Drama', 'Comedy', 'History', 'Romance', 'Adventure', 'Comedy', 'Thriller', 'Comedy', 'Crime', 'History', 'Thriller', 'Animation', 'Comedy', 'Family', 'Horror', 'Biography', 'Comedy', 'Documentary', 'Comedy', 'Crime', 'Horror', 'Mystery', 'Action', 'Biography', 'Comedy', 'Documentary', 'Action', 'Adventure', 'Comedy', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sitcom', 'Sport', 'Thriller', 'War', 'Western', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western', 'Anime']
	#movieInfo = getInfoForML(name,user)

	results.append(movieInfo[0])#imdb
	results.append(movieInfo[1])#meta
	#genres
	for i in genres:
		results.append(int(i in movieInfo[2]))
	##print str(count)+", "+str(len(results))
	results.append(movieInfo[3])#awards
	results.append(movieInfo[4])#length
	cast = getDataFromFireBaseMultiple(user,"Cast")
	for i in cast:
		try:
			results.append(int(i in movieInfo[5]))
		except:
			results.append(0)
	return results
def predictMovieMLforUser(movieInfo,user):
	info = translateForPrediction(movieInfo,user)
	#print "Got Info"
	features = getDataFromFireBaseMultiple(user,"Data")
	#print "Got Data"
	labels = getDataFromFireBaseMultiple(user,"Predictions")
	#print "Got Predictions"
	res = predict.predictMovie(info,features,labels)[0]
	if res == "Love":
		return ["Love","green"]
	if res == "Like":
		return ["Like","blue"]
	if res == "Mind":
		return ["Won't Mind it","orange"]
	return ["Hate","red"]
def login(user,passw):
	users = str(db.child("Users").get().val()).split(",")
	passwords = str(db.child("PassW").get().val()).split(",")
	for i in range(len(users)):
		if users[i] == user:
			return passwords[i] == passw
	return False
def changePassword(old,newP,user):
	users = str(db.child("Users").get().val()).split(",")
	passwords = str(db.child("PassW").get().val()).split(",")
	for i in range(len(users)):
		if users[i] == user:
			if passwords[i] == old:
				passwords[i] =newP
				db.child("PassW").set(",".join(passwords))
				return "Password Changed"
			else:
				return "Not Correct Password"
	return "Username Not Found"

def getInfoForMovieMLUP(link):
	source_code=requests.get(link)
	plain_text=source_code.text
	soup=BeautifulSoup(plain_text)
	return getInfoForMLviaLinkUP(soup)
def getInfoForMLviaLinkUP(soup):
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
	return info
def predictMovieMLforUserList(movieInfoList,user):
	info = []
	for i in movieInfoList:
		info.append(translateForPrediction(i,user))
	#print "Got Info"
	features = getDataFromFireBaseMultiple(user,"Data")
	#print "Got Data"
	labels = getDataFromFireBaseMultiple(user,"Predictions")
	#print "Got Predictions"
	return predict.predictMovieList(info,features,labels)
def deleteAccount(user,passw):
	users = str(db.child("Users").get().val()).split(",")
	passwords = str(db.child("PassW").get().val()).split(",")
	for i in range(len(users)):
		if users[i] == user:
			if passwords[i] == passw:
				del users[i]
				del passwords[i]
				db.child("Users").set(",".join(users))
				db.child("PassW").set(",".join(passwords))
				db.child(user).remove()
				return ""
			else:
				return "Incorrect Password"
	return "Username not Found"
def getRatedMovies(user):
	movies = getDataFromFireBaseMultiple(user,"Movies")
	predictions = getDataFromFireBaseMultiple(user,"Predictions")
	res = []
	for i in range(len(movies)):
		res.append([movies[i],predictions[i]])
	return res
def updateRate(user,pred):
	db.child(user).child("Predictions").set(pred)
"""
print("Starting")
start = time.time()
print addUserToFire("shoekla","chini","Baby Driver,Star Wars","The Notebook,Fifty Shades of Grey")
end = time.time()
print "Total Time:"
print(end - start)
#print getDataFromFireBaseMultiple("shoekla","Data")
print getDataFromFireBaseMultiple("shoekla","Cast")
print getDataFromFireBaseMultiple("shoekla","Movies")
"""













