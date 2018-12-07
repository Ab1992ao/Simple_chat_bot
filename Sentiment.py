# coding: utf-8
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.pipeline import Pipeline
from nltk.tokenize.casual import TweetTokenizer
import pickle
import nltk


class sentiment_model:
    def __init__(self):
        try:
            with open('C:\\Users\AlexConda\mcs-nlp\lecture1\svc_model.pickle', 'rb') as f:
                self.model = pickle.load(f)
        except:
            print('Dowload error! Model is not extract!')
            
    def give_sentiment(self, st):
        return self.model.predict_proba(st)[:,1]

