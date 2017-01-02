
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
d = len(arr)
if d == 1:
	sendMessage("1 Movie coming out today")
else:
	sendMessage(str(d)+" Movies coming out today")
for i in arr:
	sendMessage(getInfo(i))
for i in arr:
	moviesendMessage(getInfo(i))



