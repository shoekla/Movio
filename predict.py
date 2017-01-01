
from sklearn import tree

def predictMovie(info,features,labels):
	clf = tree.DecisionTreeClassifier()
	clf = clf.fit(features,labels)
	return clf.predict(info)
#print predictMovie([1,1,0],[[1,0,1],[0,0,0]],[1,0])