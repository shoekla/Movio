
from sklearn import tree

features = [[1,0,1,[1,2]],[0,1,1,[3,2]],[1,0,0,[0,9]],[1,1,0,[2,3]]]
labels = [1,1,1,1]

labels = ["You Will Love it","You Will Love it","You Will Love it","You Will Love it"]
clf = tree.DecisionTreeClassifier()
clf = clf.fit(features,labels)
print clf.predict([0,0,0,[2,3]])




