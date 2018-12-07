# -*- coding: utf-8 -*-
"""
Редактор Spyder

Это временный скриптовый файл.
"""
import re
import os
import json
import nltk
import scipy
import numpy as np
import pymorphy2
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string
from nltk.corpus import stopwords

from gensim.models import KeyedVectors

class ENGINE_3(object):
    def __init__(self):
        self.knowledge_base = json.load(open("./BC_base.json"))#json.load(open("./faq_tks.json"))
        self.lemmatizer = pymorphy2.MorphAnalyzer()
        self.w2v_model = pickle.load(open('c:\\Users\\AlexConda\\Desktop\\mcs-nlp\\call_bots\\word_vectors.pkl', "rb"))
        
        # contains correct output for each class
        self.answers = np.array([t['answer'] for t in self.knowledge_base])
        self.tfidf = self.prepare_vectorizer() 
        self.vectorized_kbase, self.class_indexes = self.vectorize_knowledge_base()
    
    def prepare_vectorizer(self):
        """
        Fits TF-IDF vectorizer using all available text from self.knowledge_base
        
        Returns TF-IDF vectorizer object
        """
        # your code goes here
        vectorizer = TfidfVectorizer(ngram_range=(1, 1), analyzer='word', min_df=1)
        all_texts = []
        for st in self.knowledge_base:
            all_texts+=[st['question']]+[st['answer']]#+st['paraphrased_questions']
        
        all_texts=[' '.join(self.tokenize_and_lemmatize(st)) for st in all_texts]
        matrix = vectorizer.fit_transform(all_texts)
        tfidf = dict(zip(vectorizer.get_feature_names(), vectorizer.idf_))
        
        return tfidf
        
    def tokenize_and_lemmatize(self, file_text):
    #firstly let's apply nltk tokenization
        tokens = nltk.word_tokenize(file_text)
        
    #let's delete punctuation symbols
        tokens = [str.lower(i) for i in tokens if ( i not in string.punctuation )]

    #deleting stop_words
        stop_words = stopwords.words('russian')
        stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на'])
        tokens = [i for i in tokens if ( i not in stop_words )]
        
    #lemmatize words
        return  [self.lemmatizer.parse(i)[0].normal_form for i in tokens]
    

    
    def bow_encoder(self,model, tokenizer, text, vsize=300):
        vec = np.zeros(vsize).reshape((1, vsize))
        tokens=tokenizer(text)
        count = 0.
        for word in tokens:
            try:
                vec += model[word].reshape((1, vsize)) * self.tfidf[word]
                count += 1.
            except KeyError: # handling the case where the token is not
                         # in the corpus. useful for testing.
                    continue
        if count != 0:
            vec /= count
        return vec[0]
    
    def vectorize(self, data):
        """
        Turns a list of N strings into their vector representation using self.w2v_model.
        In the simplest case, averages the word vectors of all words in a sentence.
        Returns a a matrix of shape [N, 300]
        """
        vectorized = []
        for d in data:
            vectorized.append(self.bow_encoder(self.w2v_model, self.tokenize_and_lemmatize, d))
        
        return np.array(vectorized)
        
    def vectorize_knowledge_base(self):
        """
        Vectorizes all questions using the vectorize function.
        Builds a list containing class number for each question.        
        """
        vectors = []
        class_labels = []
        
        for i, t in enumerate(self.knowledge_base):
            #vc = np.vstack([self.vectorize([t['question']]), self.vectorize(t['paraphrased_questions'])])
            vc = self.vectorize([t['question']])
            vectors.append(vc)
            class_labels.append(i)
            #class_labels += [i]*len(t['paraphrased_questions'])
        
        
        return np.vstack(vectors), class_labels
    
    def compute_class_scores(self, similarities):
        """
        Accepts an array of similarities of shape (self.class_indexes, )
        Computes scores for classes.
        Returns a dictionary of size (n_classes) that looks like
        {
            0: 0.3,
            1: 0.1,
            2: 0.0,
            class_n_id: class_n_score
            ...
        }
        """
        class_scores = dict(zip(range(len(self.answers)), [0]*len(self.answers)))
        
        for ci, sc in zip(self.class_indexes, similarities):
            class_scores[ci] += sc
        return class_scores
    
    def get_top(self, query, top_k=1):
        if isinstance(query, str):
            query = [query]
            
        vectorized_query = self.vectorize(query)
        css = cosine_similarity(vectorized_query, self.vectorized_kbase)[0]
        scores = self.compute_class_scores(css)
        
        sorted_scores = sorted(scores.items(), key= lambda x: x[1])[::-1][:top_k]
        top_classes = np.array([c[0] for c in sorted_scores])
        top_answers = list(self.answers[top_classes])
        if scores[top_classes[0]]<=0.5:
            top_answers=['К сожалению в системе нет ответа на Ваш вопрос. Пожайлуста, обратитесь к оператору по тел. ******']
        return top_answers