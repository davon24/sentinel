#!/usr/bin/env python3

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

import csv

import sys

_file = sys.argv[1]
#_csv = csv.reader(line.splitlines(), quotechar="'")

with open(_file, 'r') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    line_count = 0
    for row in csv_reader:
        print(row)


#_csv = csv.reader(line.splitlines())
#print(_csv)

