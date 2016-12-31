from flask import Flask, request
from twilio import twiml
import time
from flask import render_template
import movie
app = Flask(__name__)

@app.route('/movioHome/')
def goHomeMovio():
    print "He"
    return render_template("mov/home.html")



@app.route('/movioHome/', methods=['POST'])
def my_form_post(name=None, length=None,res = [],timeA = None):
    print "1"
    name = request.form['name']
    print name
    startTime=time.time()
    res = movie.getMoviesSearch(name)
    timeA = time.time() - startTime
    length = str(len(res))
    return render_template('mov/results.html',name=name,timeA=timeA,res=res,length=length)








#This method will take care of all cases where user texts twilio phone number
@app.route('/sms/',methods=["POST"])
def sms():
    message_body = request.form['BODY']
    #gets "info on" a movie that user send Ex: "info on inception"
    if message_body[:7] == "info on":
        arr = message_body.split(" ")
        s = ' '.join(arr[2:])
        info = str(movie.getInfo(s))
        resp = twiml.Response()
        resp.message("\n{}".format(info))
        return str(resp)
    #more just gets sample commands for user to send (I will add to it later)
    if message_body == "more":
        resp = twiml.Response()
        resp.message("Sample Commands:\n info on [MOVIE NAME]")
        return str(resp)
    resp = twiml.Response()
    resp.message("I did not understand that, text more for sample commands")
    return str(resp)
if __name__ == '__main__':
	app.run()