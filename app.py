from flask import Flask, request
from twilio import twiml
import time
from flask import redirect
from flask import render_template
import movie
app = Flask(__name__)
#Home of app
@app.route('/movioHome/')
def goHomeMovio():
    print "He"
    return render_template("mov/home.html")
#Test For Texting service
@app.route('/homesms/')
def hoemfsdfgsdfgsoms():
    return render_template("mov/homeSMS.html")
#Search For Movies
@app.route('/movioHome/', methods=['POST'])
def my_form_post(name=None, length=None,res = [],timeA = None):
    print "1"
    try:
        name = str(request.form['name']).strip()
        print name
        startTime=time.time()
        res = movie.getMoviesSearch(name)
        for i in res:
            if "\xc3" in i:
                res.remove(i)
        print res
        timeA = time.time() - startTime
        length = str(len(res))
        return render_template('mov/results.html',name=name,timeA=timeA,res=res,length=length)
    except Exception as e:
        print str(e)

#adds movie via flask web app
@app.route('/movioHome/addMovie/', methods=['POST'])
def addMovieToML(name=None,like=None):
    name = str(request.form['name']).strip()
    print name
    if name.endswith(": 0") or name.endswith(": 1"):
        name = name[:-3]
    like = int(request.form['like'])
    movie.addToML(name,like)
    return redirect("http://127.0.0.1:5000/movioHome/myMovies/")

#displays all mvoies learned to user
@app.route('/movioHome/myMovies/')
def myMovies(arr=None):
    arr = []
    arr = movie.getMyMovies()
    return render_template("mov/movies.html",arr=arr)


@app.route('/movio/addUser/<name>/')
def addUserInApp(name):
    try:
        movie.addUser(name)
        return "All Good!"
    except:
        return "Error"
@app.route('/movio/message/<user>/<message_body>')
def getResponseForUser(user,message_body,res = None):
    try:
        res = ""
        if "will i like" in message_body:
            arr = message_body.split(" ")
            res = " ".join(arr[3:])
            return str(movie.predictMovieMLforUser(res,user))
        elif "i like" in message_body:
            arr = message_body.split(" ")
            res = " ".join(arr[2:])
            movie.addToMLForUser(res,1,user)
            return str("Learned that you liked "+res)
        elif "i did not like" in message_body:
            arr = message_body.split(" ")
            res = " ".join(arr[4:])
            movie.addToMLForUser(res,0,user)
            return str("Learned That You did not liked "+res)
        elif "info on " in message_body or "information " in message_body:
            arr = message_body.split(" ")
            res = " ".join(arr[2:])
            return str(movie.getImdbLink(res))
        return str("I did not understand that, text more for sample commands")
    except:
        return str("Error Occured Please Try Again Later")

#This method will take care of all cases where user texts twilio phone number
@app.route('/sms/',methods=["POST"])
def sms():
    message_body = str(request.form['BODY']).lower().strip()
    #gets "info on" a movie that user send Ex: "info on inception"
    try:
        if message_body[:7] == "info on":
            arr = message_body.split(" ")
            s = ' '.join(arr[2:])
            info = str(movie.getInfo(s))
            resp = twiml.Response()
            resp.message("\n{}".format(info))
            return str(resp)
        if "will i like" in message_body:
            arr = message_body.split(" ")
            res = " ".join(arr[3:])
            resp = twiml.Response()
            resp.message(movie.predictMovieML(res))
            return str(resp)
        elif "i like" in message_body:
            arr = message_body.split(" ")
            res = " ".join(arr[2:])
            movie.addToML(res,1)
            resp = twiml.Response()
            resp.message("Learned that you liked "+res)
            return str(resp)
        elif "i did not like" in message_body:
            arr = message_body.split(" ")
            res = " ".join(arr[4:])
            movie.addToML(res,0)
            resp = twiml.Response()
            resp.message("Learned That You did not liked "+res)
            return str(resp)
        #more just gets sample commands for user to send (I will add to it later)
        if message_body == "more":
            resp = twiml.Response()
            resp.message("Sample Commands:\n info on [MOVIE NAME]\n i like [MOVIE NAME]\n I did not like [MOVIE NAME]\n Will I like [MOVIE NAME]")
            return str(resp)
        resp = twiml.Response()
        resp.message("I did not understand that, text more for sample commands")
        return str(resp)
    except Exception as e:
        print str(e)    
if __name__ == '__main__':
	app.run()