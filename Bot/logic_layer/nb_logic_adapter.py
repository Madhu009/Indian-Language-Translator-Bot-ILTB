from input_layer import Input
from logic_layer import LogicAdapter
from datetime import datetime

class NBLogicAdapter(LogicAdapter):

    def __init__(self,**kwargs):
        super(NBLogicAdapter,self).__init__(**kwargs)
        from nltk import NaiveBayesClassifier
        self.positive = [
            'what time is it',
            'do you know the time',
            'do you know what time it is',
            'what is the time'
        ]

        self.negative = [
            'it is time to go to sleep',
            'what is your favorite color',
            'i had a great time',
            'what is'
        ]

        labeled_data=([(text,0)for text in self.negative]+
                      [(text,1)for text in self.positive])


        train_set = [(self.extract_features(text), cls) for (text, cls) in labeled_data]

        self.classifier = NaiveBayesClassifier.train(train_set)

        # print(train_set)
        #(list(tuples))
        #(list(dict,0/1))

    def extract_features(self, text):
        """
        Provide an analysis of significan features in the string.
        """
        features = {}


        all_words = " ".join(self.positive + self.negative).split()

        for word in text.split():
            features['contains({})'.format(word)] = (word in all_words)

        for letter in 'abcdefghijklmnopqrstuvwxyz':
            features['count({})'.format(letter)] = text.lower().count(letter)
            features['has({})'.format(letter)] = (letter in text.lower())

        return features

    def process(self, statement):

        features = self.extract_features(statement.text.lower())
        #{'contains(ki)': False, 'contains(hal)': False, 'contains(hai)': False, 'count(a)': 2, 'has(a)': True, 'count(b)': 0, 'has(b)': False, 'count(c)': 0, 'has(c)': False, 'count(d)': 0, 'has(d)': False, 'count(e)': 0, 'has(e)': False, 'count(f)': 0, 'has(f)': False, 'count(g)': 0, 'has(g)': False, 'count(h)': 2, 'has(h)': True, 'count(i)': 2, 'has(i)': True, 'count(j)': 0, 'has(j)': False, 'count(k)': 1, 'has(k)': True, 'count(l)': 1, 'has(l)': True, 'count(m)': 0, 'has(m)': False, 'count(n)': 0, 'has(n)': False, 'count(o)': 0, 'has(o)': False, 'count(p)': 0, 'has(p)': False, 'count(q)': 0, 'has(q)': False, 'count(r)': 0, 'has(r)': False, 'count(s)': 0, 'has(s)': False, 'count(t)': 0, 'has(t)': False, 'count(u)': 0, 'has(u)': False, 'count(v)': 0, 'has(v)': False, 'count(w)': 0, 'has(w)': False, 'count(x)': 0, 'has(x)': False, 'count(y)': 0, 'has(y)': False, 'count(z)': 0, 'has(z)': False}

        confidence = self.classifier.classify(features)

        response=Input('output text')
        response.confidence=confidence
        return response