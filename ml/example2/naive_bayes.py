#!/usr/bin/env python3

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

import csv

import sys

_file = sys.argv[1]

#https://docs.python.org/3/library/codecs.html#standard-encodings

with open(_file, newline='', encoding='latin-1') as csvfile:
#with open(_file, newline='', encoding='cp1252') as csvfile:
#with open(_file, encoding='ISO-8859-1') as csvfile:
#with open(_file, encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    csv_list = list(csv_reader)
    #print(_list[1:])

#print(csv_list)

X = []
y = []

for line in csv_list:
    #print(line)
    #print(line[0])
    #print(line[1])
    if line[0] == 'ham':
        #print('ok')
        v1=0
    else:
        #print('SPAM')
        v1=1

    y.append(v1)
    X.append(line[1])


X_train, X_test, y_train, y_test = train_test_split(X, y)
vectorizer = CountVectorizer()

#print(X_train)
#counts = vectorizer.fit_transform(X_train.values)
counts = vectorizer.fit_transform(X_train)

classifier = MultinomialNB()
#targets = y_train.values
targets = y_train
classifier.fit(counts, targets)

_sample = sys.argv[2]

sample_file = open(_sample, 'r')
sample = []
for line in sample_file:
    sample.append(line)

#data = s.read()
#f.close()
##print(data)

#s = '''
#URGENT! Your Mobile No. was awarded <E5><A3>2000 Bonus Caller Prize on 5/9/03 This is our final try to contact U! Call from Landline 09064019788 BOX42WR29C, 150PPM
#'''
#data = [ s ]

sample_count = vectorizer.transform(sample)
predictions = classifier.predict(sample_count)
print(predictions)


#reader = csv.reader(open(_file, encoding='utf-8'))
#for line in reader:
#    print(line)
#_csv = csv.reader(line.splitlines(), quotechar="'")

#with open(_file, encoding='utf-8') as csvfile:
#    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
#    for row in csv_reader:
#        print(', '.join(row))
#
#    #print(csv_reader)
#    #line_count = 0
#    #_line = list(csv_reader)
#    #print(_line)
#
#
##_csv = csv.reader(line.splitlines())
##print(_csv)

