from random import randint
import numpy as np
from sklearn.naive_bayes import *

class NaiveBayes:
	''' A simple Naive Bayes to determine if work done is good.'''
	nb_classifier = GaussianNB()

	def train_classifier(self):
		goodData = self.generateDataPoints(1000)
		badData = self.generateDataPoints(1000, good=False)

		X = np.concatenate((goodData, badData))
		y = np.chararray(2000)

		for i in xrange(0, 1000):
			np.put(y, i, "V")
		for i in xrange(1000, 2000):
			np.put(y, i, "I")

		self.nb_classifier = self.nb_classifier.fit(X,y)

	def classify(self, numEvents, timeSpent, logEvents):
		result = self.nb_classifier.predict([np.array([numEvents, timeSpent, logEvents], dtype='f')])[0]

		if result == 'V':
			return True
		else:
			return False

	def generateDataPoints(self, numPoints, good=True):
		data = np.zeros((1000, 3))

		for i in xrange(0, numPoints):
			if good == True:
				numEvents = randint(150, 500)
				timeSpent = randint(240, 400)
				logEvents = randint(300, 1000)
			else:
				numEvents = randint(0, 100)
				timeSpent = randint(0, 150)
				logEvents = randint(0, 200)

			np.copyto(data[i], np.array([numEvents, timeSpent, logEvents]))

		return data