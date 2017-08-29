from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
import time
import os
import movie
import userData
import re
app = Flask(__name__)

@app.route('/')
def login():
	return render_template("login.html")

@app.route('/signUp/')
def signUp():
	return render_template("signUp.html")
@app.route('/signUp/',methods=['POST'])
def signUpUser(userName = None, passw = None, likedMovies = None, hateMovies = None):
	print "Signing up"
	try:
		userName = request.form["name"]
		passw = request.form['passw']
		likedMovies = request.form['lm']
		hateMovies = request.form['hm']
		if re.match('^[\w-]+$', userName) is None:
			return render_template("signUp.html",userName=userName,passw=passw,likedMovies=likedMovies,hateMovies = hateMovies,message="Only Alpha Numeric Characters")
		
		if (userData.addUserToFire(userName,passw,likedMovies,hateMovies)):
			return render_template("login.html",message="Account Created",color="green")
		else:
			return render_template("signUp.html",userName=userName,passw=passw,likedMovies=likedMovies,hateMovies = hateMovies,message="User Name already taken :(")
	except Exception as e: print(e)
@app.route('/ratedMovies/',methods=['POST'])
def goToRated(userName=None,results = [],length=0):
	userName = request.form["userName"]
	results = userData.getRatedMovies(userName)
	length = len(results)
	#print results
	return render_template("rated.html",userName=userName,results=results,length=length)

@app.route('/updateRatings/',methods=['POST'])
def Rate(userName=None,results = [],length=0):
	userName = request.form["userName"]
	length = int(request.form["length"])
	results = []
	#print "1"
	for i in range(length):
		results.append(request.form[str(i)])
	#print results
	userData.updateRate(userName,results)
	results = userData.getRatedMovies(userName)
	return render_template("rated.html",userName=userName,results=results,length=length,message="Ratings Updated!")

@app.route('/accountSett/',methods=['POST'])
def gotoAccountSett(userName = None):
	userName = request.form["userName"]
	return render_template("account.html",userName = userName)
@app.route('/accountSettPass/',methods=['POST'])
def gotoAccountSettChangePass(userName = None,old=None,newP=None,message = None):
	userName = request.form["userName"]
	old = request.form["old"]
	newP = request.form["newP"]
	message = userData.changePassword(old,newP,userName)
	return render_template("account.html",userName = userName,message=message)
@app.route('/delete/',methods=['POST'])
def gotoAccountSettDelte(userName = None,passw=None,messageP = None):
	userName = request.form["userName"]
	passw = request.form["passw"]
	messageP = userData.deleteAccount(userName,passw)
	if len(messageP) == 0:
		return render_template("login.html",message="Account Deleted",color="red")
	return render_template("account.html",userName = userName,messageP=messageP)
@app.route('/home/',methods=['POST'])
def goHome(movies = [],userName=None,passw = None,pData = [],pRes = []):
	try:
		#print "Home"
		print("Starting")
		start = time.time()
		userName = request.form["name"]
		passw = request.form['passw']
		if (userData.login(userName,passw)):
			movies = movie.getWeekMoviesList()
			for i in movies:
				for s in i:
					if movie.isEnglish(s) == False:
						movies.remove(i)
			#print movies[0][7]
			for i in movies:
				try:
					pData.append(userData.predictMovieMLforUser(userData.getInfoForMovieMLUP("http://www.imdb.com"+i[7]),userName))
				except:
					pData.append(["Unknown","grey"])
			end = time.time()
			print "Total Time:"
			print(end - start)
			try:
				return render_template("home.html",movies = movies,userName = userName,pData=pData)
			except:
				return render_template("home.html",movies = [],userName = userName,pData=[])
		else:
			return render_template("login.html",message="Invalid Login Credentials",color="red")
	except Exception as e:
		return "Error Occured"
@app.route('/search/',methods=['POST'])
def getSearch(name = None, results = [],length = 0,userName=None):
	try:
		userName = request.form["userName"]
		name = request.form["name"].lower()
		results = movie.getMoviesSearch(name)
		length = len(results)
		return render_template("list.html",name=name,results = results,length = length,userName=userName)
	except Exception as e: print(e)

@app.route('/movie/',methods=['POST'])
def getMovieDetailsPage(name = None, data = None, link = None,trailer = None,ml = [],genre = None,people=None,summary = None,results = [],userName=None,prediction = [],message=None,like = None):
	try:
		name = request.form["name"]
		data = request.form["data"]
		link = request.form["link"]
		userName = request.form["userName"]
		#print link
		trailer = movie.getTrailer(name)
		goog = movie.getGoogLink(name)

		ml,summary,results =  movie.getInfoForMovieML("http://www.imdb.com"+link)
		genre = ", ".join(ml[2])
		people = ", ".join(ml[5])
		message = ""
		like = userData.checkMovieRating(userName,name) 
		if like != None:
			message = "r"
			if like == "Love":
				prediction = ["Love","green"]
			if like == "Like":
				prediction = ["Like","blue"]
			if like == "Mind":
				prediction = ["Won't Mind it","orange"]
			if like == "Hate":
				prediction = ["Hate","red"]
		else:
			prediction = userData.predictMovieMLforUser(ml,userName)
		#print "OK"
		#return "Name: "+name+", Data: "+data+", Link: "+link
		try:
			return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people=people,summary = summary,results=results,userName = userName,prediction=prediction,message=message)
		except:
			try:
				return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people=people,summary = summary,results=[],userName = userName,prediction=prediction,message=message)
			except:
				try:
					return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people="",summary = "",results=[],userName = userName,prediction=prediction,message=message)
				except:
					return render_template("detail.html",name=name,data=data,trailer=trailer,ml = [],link = link,goog=goog,genre = genre,people="",summary = "",results=[],userName = userName,prediction=prediction,message=message)
	except:
		return redirect("http://www.imdb.com"+link)
@app.route('/rateMovie/',methods=['POST'])
def rateMovie(name = None, data = None, link = None,trailer = None,ml = [],genre = None,people=None,summary = None,results = [],userName=None,prediction = [], message = None,noUse=None,noUse2=None):
	ml = eval(request.form["ml"])
	if len(ml) == 0:
		ml,noUse,noUse2 = movie.getInfoForMovieML("http://www.imdb.com"+link)
	name = request.form["name"]
	data = request.form["data"]
	link = request.form["link"]
	userName = request.form["userName"]
	trailer = request.form["trailer"]
	goog = request.form["goog"]
	summary = request.form["summary"]
	results = eval(request.form["results"])
	genre = request.form["genre"]
	people = request.form["people"]
	prediction = eval(request.form["prediction"])
	like = request.form["like"]
	if like == "1":
		return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people=people,summary = summary,results=results,userName = userName,prediction=prediction,message = "p")
	try:
		userData.addToMLForUser(ml,like,userName,name)
		if like == "Love":
			prediction = ["Love","green"]
		if like == "Like":
			prediction = ["Like","blue"]
		if like == "Mind":
			prediction = ["Won't Mind it","orange"]
		if like == "Hate":
			prediction = ["Hate","red"]
		return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people=people,summary = summary,results=results,userName = userName,prediction=prediction,message = "r")
	except:
		return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people=people,summary = summary,results=results,userName = userName,prediction=prediction,message = "e")
	return userName

@app.route('/upMovie/',methods=['POST'])
def getMovieDetailsPageUp(name = None, data = None, link = None,trailer = None,ml = [],genre = None,people=None,summary = None,results = [],userName=None,prediction = []):
	#print "Movie Upcoming"
	try:
		name = request.form["name"]
		userName = request.form["userName"]

		data = request.form["data"]
		data = name[name.find(" (")+1:]

		name = name[:name.find(" (")]
		link = request.form["link"]
		summary = request.form["summary"]
		trailer = movie.getTrailer(name)
		goog = movie.getGoogLink(name)
		ml,results =  movie.getInfoForMovieMLUp("http://www.imdb.com"+link)
		message = ""
		like = userData.checkMovieRating(userName,name) 
		if like != None:
			message = "r"
			if like == "Love":
				prediction = ["Love","green"]
			if like == "Like":
				prediction = ["Like","blue"]
			if like == "Mind":
				prediction = ["Won't Mind it","orange"]
			if like == "Hate":
				prediction = ["Hate","red"]
		else:
			prediction = userData.predictMovieMLforUser(ml,userName)
			genre = ", ".join(ml[2])
			people = ", ".join(ml[5])

		#print "OK"
		#return "Name: "+name+", Data: "+data+", Link: "+link
		try:
			return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people=people,summary = summary,results=results,userName = userName,prediction=prediction,message=message)
		except:
			try:
				return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people=people,summary = summary,results=[],userName = userName,prediction=prediction,message=message)
			except:
				try:
					return render_template("detail.html",name=name,data=data,trailer=trailer,ml = ml,link = link,goog=goog,genre = genre,people="",summary = "",results=[],userName = userName,prediction=prediction,message=message)
				except:
					return render_template("detail.html",name=name,data=data,trailer=trailer,ml = [],link = link,goog=goog,genre = genre,people="",summary = "",results=[],userName = userName,prediction=prediction,message=message)
		
	except Exception as e:
		return redirect("http://www.imdb.com"+link)



if __name__ == '__main__':
    app.run()






"""
@app.route('/carpool/search/',methods=['POST'])
def getCarSearch(name = None, arr = None, dep = None, trips = None):
	name = request.form["name"].lower()
	arr = request.form["arr"].lower()
	dep = request.form["dep"].lower()
	print "Name: "+name
	print "Arr: "+arr
	print "Dep: "+dep
	print "Search"
	trips = []
	trips = car.search(name,arr,dep)
	return render_template("carpool/list.html",trips = trips)

@app.route("/carpool/add/")
def addCarTrip():
	return render_template("carpool/add.html")

@app.route("/carpool/<name>/")
def detailCarForUserTrip(name,departure=None,arrival=None,price=None,numSeats=None,bags=None,summ=None,youInfo=None,departDate = None,googleA = None, googleD = None):
	print "Some"
	price,departure,arrival,numSeats,bags,departDate,summ,youInfo = car.getTripInfo(name)
	googleD = departure.replace(" ","+")
	googleA = arrival.replace(" ","+")
	print "2"
	return render_template("carpool/detail.html",name=name,price = price,departure=departure,arrival=arrival,numSeats=numSeats,departDate=departDate,bags=bags,summ=summ,youInfo=youInfo,googleA=googleA,googleD = googleD)
@app.route("/carpool/tripLogin/")
def loginCarToTrip():
	return render_template("carpool/login.html")
@app.route('/carpool/loginTrip/',methods=['POST'])	
def tripCarLoginAccount(name = None,passw = None,applicants = None):
	name = str(request.form["name"])
	passw = str(request.form["passw"])
	print name,passw
	print "Okar"
	if car.tripLoginCheck(name,passw):
		print "4th"
		applicants = []
		print "third"
		applicants = car.getApplicants(name)
		print "Second to last"
		return render_template("carpool/passengers.html",applicants = applicants,name=name)
	else:
		
		return render_template("carpool/login.html",mess="Invalid Credentials")
@app.route('/carpool/deleteApp/',methods=['POST'])
def deleteCarApplicants(tripName = None, name = None,applicants = None):
	name = str(request.form["name"])
	tripName = str(request.form["tripName"])
	car.deleteApplicant(tripName,name)
	name = tripName
	applicants = []
	print "third"
	applicants = car.getApplicants(name)
	print "Second to last"
	return render_template("carpool/passengers.html",applicants = applicants,name=name)


@app.route('/carpool/addTrip/',methods=['POST'])
def addTheTripCar(name = None,departure=None,arrival=None,price=None,numSeats=None,tripPass=None,bags=None,summ=None,youInfo=None,departDate = None,closeDate = None):
	name = request.form['name']
	departure = request.form['departure']
	arrival = request.form['arrival']
	price = request.form['price']
	numSeats = request.form['numSeats']
	tripPass = request.form['tripPass']
	bags = request.form['bags']
	summ = request.form['summ']
	youInfo = request.form['youInfo']
	departDate = request.form['departDate']
	closeDate = request.form['AppDead']
	print "Name: "+str(name)
	print "Departure: "+str(departure)
	print "Arrival: "+str(arrival)
	print "Price: "+str(price)
	print "numSeats: "+str(numSeats)
	print "tripPass: "+str(tripPass)
	print "bags: "+str(bags)
	print "Departure Date: "+str(departDate)
	print "App Close Date: "+str(closeDate)
	print "summ: "+str(summ)
	print "youInfo: "+str(youInfo)
	print "DONE --------------------------------------"
	if car.addTrip(name,departure,arrival,price,numSeats,tripPass,bags,summ,youInfo,departDate,closeDate) == "Error":
		return render_template("carpool/add.html",mess="Trip Name already in system")
	return render_template("carpool/succ.html",tripPass=tripPass,name=name)

@app.route('/carpool/applyForTrip/',methods=['POST'])
def applyforthetripCar(name = None, email= None, phone = None,tripName = None,mess = None):
	name = request.form["name"]
	email = request.form["email"]
	phone = request.form["phone"]
	tripName = request.form["tripName"]
	mess = request.form["mess"]
	print "Name: "+name
	print "Email: "+email
	print "Phone: "+phone
	print "Trip Name: "+tripName
	print "Message: "+mess
	try:
		car.addApplicant(tripName,name,phone,email,mess)
		return render_template("carpool/seccApply.html",tripName=tripName)
	except:
		return render_template("carpool/error.html")
"""





