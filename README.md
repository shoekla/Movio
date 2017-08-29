# Movio
Movio is a python script that texts (via twilio api) you everyday whichever movies come out that day along with.
Also, if it is Monday it texts you a list of all movies coming out that week.
It uses imdb and youtube to get ratings, trailers and other information.
It also uses machine learning (scikit-learn) to learn your taste in movies.<br/>
Web Application: https://movioe.herokuapp.com/
# Texting service
Simply create a twilio account, set some variables to the keys you receive, and deploy this flask application to get the texting service ready
# Android Application
Android app is voice driven (meaning you just give the app voice commands) and the app communicates to the flask application to learn which movies users like and which movies they do not. Finally, the app can predict which movies the user will like in the future (accuracy is a reflection on the quantity and quality of the data given previously)
# Web Application
Movio is also a web application which has the same functionality as the android apllication, buts works within flask to make the ml faster. It also adds different levels of liking a movie. It learns movies one by one (unlike the android application that learns movies in groups at a time), this makes the web app have a more fluent process in which the user feeds data to the ml algorithm.
# Machine Learning algorithm
This application utilized the K nearest neighbors algorithm that allows simple addition of data and a relatively simple way of prediction.
Below is an image I created to hopefully give you a good idea on how it works. I used this over a decision tree, because it was faster for the test cases I ran on it with the same accuracy and since decision trees are usually used just to visualize the algorithm in a simple way.
<img src="https://docs.google.com/drawings/d/13-lHtxaBa3ngKoffD-RudUMFZTyQt2gwk6Wf8R4j__w/pub?w=960&h=720"/>
