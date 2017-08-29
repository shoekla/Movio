#!/usr/bin/env python -W ignore::DeprecationWarning
from sklearn import tree
import numpy as np
def predictMovie(info,features,labels):
	clf = tree.DecisionTreeClassifier()
	clf = clf.fit(features,labels)
	return clf.predict(np.array(info).reshape(1,-1))
def predictMovieList(infoList,features,labels):
	clf = tree.DecisionTreeClassifier()
	clf = clf.fit(features,labels)
	res = []
	for i in infoList:
		res.append(clf.predict(i)[0])
	return res



from sklearn.neighbors import KNeighborsClassifier
#testing, training Data, traing Results
def predictMovieKNN(info,features,labels):
	neigh = KNeighborsClassifier(n_neighbors=3)
	neigh.fit(features, labels) 
	return neigh.predict(info)
#print predictMovie([1,1,0], [[1,0,1],[0,0,0]],  ["Love","Hate"])



