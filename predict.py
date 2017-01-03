
from sklearn import tree

def predictMovie(info,features,labels):
	clf = tree.DecisionTreeClassifier()
	clf = clf.fit(features,labels)
	return clf.predict(info)




from sklearn.neighbors import KNeighborsClassifier
def predictMovieKNN(info,features,labels):
	neigh = KNeighborsClassifier(n_neighbors=3)
	neigh.fit(features, labels) 
	return neigh.predict(info)
#print predictMovie([1,1,0],[[1,0,1],[0,0,0]],[1,0])