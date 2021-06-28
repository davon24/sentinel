
# supervised machine learning with syslog data (sklearn) MacOS   

supervised learning with naive bayes algorithms  
https://scikit-learn.org/stable/modules/classes.html#module-sklearn.naive_bayes  

These are supervised learning methods based on applying Bayes’ theorem with strong (naive) feature independence assumptions.    

---
## Install/Setup
requires python 3.8 or newer
```
pip3 install sentinel-server
```
requires [sklearn](https://scikit-learn.org)  
```
pip3 install -U scikit-learn   
```

This demo/doc is on MacOS log stream

---    
We'll start by capturing 3000 lines of syslog data...  
taking a small sample to build a training set for our model.   
```  
sentinel sample-logstream 3000   
```  

Now that we have a basic set of data to work with,   
we need to comb through this data.    

Identify and mark anything that would be recognizable as pattern.   
In our case, we'll look for any errors, faults, or concerns...    
```  
sentinel list-training
```    

An example of a message in our training data that has an error,    
rowid 124,  tag '0'   
```
(124, '0', '{"traceID":424856721912238084,"eventMessage":"error: XPC: synchronousRemoteObjectProxyWithErrorHandler encountered error: Error Domain=NSCocoaErrorDomain Code=4099 \\"The connection to service on pid 0 named com.apple.Maps.MapsSync.store was invalidated.\\" UserInfo={NSDebugDescription=The connection to service on pid 0 named com.apple.Maps.MapsSync.store was invalidated.}","eventType":"logEvent","source":null,"formatString":"%{public}s: %{public}s\\n","activityIdentifier":0,"subsystem":"com.apple.coredata","category":"error","threadID":22252,"senderImageUUID":"76179A55-CA89-3967-A0A7-C419DB735983","backtrace":{"frames":[{"imageOffset":3466575,"imageUUID":"76179A55-CA89-3967-A0A7-C419DB735983"}]},"bootUUID":"","processImagePath":"\\/usr\\/libexec\\/routined","timestamp":"2021-01-28 09:48:53.963884-0800","senderImagePath":"\\/System\\/Library\\/Frameworks\\/CoreData.framework\\/Versions\\/A\\/CoreData","machTimestamp":1380234956447,"messageType":"Error","processImageUUID":"31C8CE8F-CF2C-3F3F-9589-5378221FA202","processID":397,"senderProgramCounter":3466575,"parentActivityIdentifier":0,"timezoneName":""}\n')
```   

We are using a binary 0 or 1 to tag our data.  All the sample-logstream data came in pre-marked as '0'.    
Now we'll inspect the data and tag any pieces of data that match our criteria.    
We'll tag such messages with a '1'    
```
sentinel update-training-tag 124 1
```

Once all 3000 samples have been reviewed and marked either '0' or '1',    
this is our base model.    
I manually tagged 114 different rowids and we'll train our program and adjust the data as necessary.   

---

We'll run two classifiers simultaneously so we can compare and contrast.    
Syslog data is text, so we'll use naive_bayes MultinomialNB and BernoulliNB    

naive_bayes.MultinomialNB (Naive Bayes classifier for multinomial models)    
The multinomial Naive Bayes classifier is suitable for classification with discrete features (e.g., word counts for text classification).    
https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html    

naive_bayes.BernoulliNB (Naive Bayes classifier for multivariate Bernoulli models)    
Like MultinomialNB, this classifier is suitable for discrete data. The difference is that while MultinomialNB works with occurrence counts, BernoulliNB is designed for binary/boolean features.    
https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.BernoulliNB.html    


Configure the program to use these algorithms and "watch" the incoming syslog data.    
```
sentinel update-config watch-syslog-sklearn-1 '{"config":"logstream","logfile":"stream","sklearn":[{"naive_bayes.MultinomialNB":["eventMessage","messageType","category"]},{"naive_bayes.BernoulliNB":["eventMessage","messageType","category"]}]}'
```

The data is in json format.  key/value pairs.     
We'll use keys eventMessage, messageType, and category for the scope of our data.    

We instantiate the algorithms and model by running the sentinel program in sentry mode.  there is a verbose mode.    
```
python3.8 -m sentinel_server sentry --verbose
```
```
sentinel sentry
```


The sentinel program reads in the training set (sentinel list-training) and displays how many records and how many are tagged as '1'   
```
sentinel Feb 01 10:06:30 tools.py INFO: Sentry watch-syslog naive_bayes.MultinomialNB
sentinel Feb 01 10:06:30 tools.py INFO: naive_bayes.MultinomialNB training records 3000 tagged 114 scope ['eventMessage', 'messageType', 'category']
sentinel Feb 01 10:06:30 tools.py INFO: Sentry watch-syslog naive_bayes.BernoulliNB
sentinel Feb 01 10:06:31 tools.py INFO: naive_bayes.BernoulliNB training records 3000 tagged 114 scope ['eventMessage', 'messageType', 'category']
```

---

Now that the program has read all the training data and instantiated each classifier,    
every new line of syslog data is run through the classifier.predict() function    
which returns a '0' or '1'    

A '1' is a prediction.    

Predictions are saved in the occurrence table.    
```
sentinel list-occurrence
```

false-positive https://en.wikipedia.org/wiki/False_positives_and_false_negatives    
Modeling here is basically eliminating false-positives.    

We may find occurrences that are predicted as '1', but are not a concern.    
```
sentinel list-occurrence naive_bayes.MultinomialNB-f01910b0a4ecd16c2632dcb78cd8f4b0b362ab7b
('naive_bayes.MultinomialNB-f01910b0a4ecd16c2632dcb78cd8f4b0b362ab7b', 21, '{"traceID":5567583286198276,"eventMessage":"LQM-WiFi:TX(58:D9:D5:2F:4C:65) AC<SU MS NB NRS NA CM EX TF FFP MRET FLE> BE<0 0 0 0 0 0 0 0 0 0 0> (5000ms)","eventType":"logEvent","source":null,"formatString":"LQM-WiFi:TX(%02X:%02X:%02X:%02X:%02X:%02X) AC<SU MS NB NRS NA CM EX TF FFP MRET FLE> %s<%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld> (%llums)\\n","activityIdentifier":0,"subsystem":"","category":"","threadID":1717080,"senderImageUUID":"0E77C487-4C15-3458-AAFA-A9224B8A5D67","backtrace":{"frames":[{"imageOffset":894250,"imageUUID":"0E77C487-4C15-3458-AAFA-A9224B8A5D67"}]},"bootUUID":"","processImagePath":"\\/kernel","timestamp":"2021-01-31 21:17:26.816110-0800","senderImagePath":"\\/System\\/Library\\/Extensions\\/IO80211FamilyV2.kext\\/Contents\\/MacOS\\/IO80211FamilyV2","machTimestamp":615478952438929,"messageType":"Default","processImageUUID":"82E2050C-5936-3D24-AD3B-EC4EC5C09E11","processID":0,"senderProgramCounter":894250,"parentActivityIdentifier":0,"timezoneName":""}\n')
```

The above piece of data is not an error or fault.  The data is simply wifi activity.      
Training this model on syslog data is not much different than training your every day spam filter.  
Instead of viagra, we're training our model on patterns or words with error or fault.    

So, we'll need to adjust our model in order to eliminate this false-positive,   
We can add this occurrence to the training data and mark it with the appropriate tag.     
```
sentinel copy-occurrence naive_bayes.MultinomialNB-f01910b0a4ecd16c2632dcb78cd8f4b0b362ab7b
```
```
sentinel list-training |grep naive_bayes.MultinomialNB-f01910b0a4ecd16c2632dcb78cd8f4b0b362ab7b
(3001, 'naive_bayes.MultinomialNB-f01910b0a4ecd16c2632dcb78cd8f4b0b362ab7b', '{"traceID":5567583286198276,"eventMessage":"LQM-WiFi:TX(58:D9:D5:2F:4C:65) AC<SU MS NB NRS NA CM EX TF FFP MRET FLE> BE<0 0 0 0 0 0 0 0 0 0 0> (5000ms)","eventType":"logEvent","source":null,"formatString":"LQM-WiFi:TX(%02X:%02X:%02X:%02X:%02X:%02X) AC<SU MS NB NRS NA CM EX TF FFP MRET FLE> %s<%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld> (%llums)\\n","activityIdentifier":0,"subsystem":"","category":"","threadID":1717646,"senderImageUUID":"0E77C487-4C15-3458-AAFA-A9224B8A5D67","backtrace":{"frames":[{"imageOffset":894250,"imageUUID":"0E77C487-4C15-3458-AAFA-A9224B8A5D67"}]},"bootUUID":"","processImagePath":"\\/kernel","timestamp":"2021-01-31 21:18:16.824507-0800","senderImagePath":"\\/System\\/Library\\/Extensions\\/IO80211FamilyV2.kext\\/Contents\\/MacOS\\/IO80211FamilyV2","machTimestamp":615528960064307,"messageType":"Default","processImageUUID":"82E2050C-5936-3D24-AD3B-EC4EC5C09E11","processID":0,"senderProgramCounter":894250,"parentActivityIdentifier":0,"timezoneName":""}\n')
```    
Assign this new piece of training data (rowid 3001) with a tag value of '0'.    
```
sentinel update-training-tag 3001 0
```    
```
sentinel list-training 3001    
(3001, '0', '{"traceID":5567583286198276,"eventMessage":"LQM-WiFi:TX(58:D9:D5:2F:4C:65) AC<SU MS NB NRS NA CM EX TF FFP MRET FLE> BE<0 0 0 0 0 0 0 0 0 0 0> (5000ms)","eventType":"logEvent","source":null,"formatString":"LQM-WiFi:TX(%02X:%02X:%02X:%02X:%02X:%02X) AC<SU MS NB NRS NA CM EX TF FFP MRET FLE> %s<%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld> (%llums)\\n","activityIdentifier":0,"subsystem":"","category":"","threadID":1717646,"senderImageUUID":"0E77C487-4C15-3458-AAFA-A9224B8A5D67","backtrace":{"frames":[{"imageOffset":894250,"imageUUID":"0E77C487-4C15-3458-AAFA-A9224B8A5D67"}]},"bootUUID":"","processImagePath":"\\/kernel","timestamp":"2021-01-31 21:18:16.824507-0800","senderImagePath":"\\/System\\/Library\\/Extensions\\/IO80211FamilyV2.kext\\/Contents\\/MacOS\\/IO80211FamilyV2","machTimestamp":615528960064307,"messageType":"Default","processImageUUID":"82E2050C-5936-3D24-AD3B-EC4EC5C09E11","processID":0,"senderProgramCounter":894250,"parentActivityIdentifier":0,"timezoneName":""}\n')
```    

Once the model has been adjusted, you have re-initialize the program on the new model.  This new model now has 3001 entries and 114 that are tagged '1'.     
```    
python3.8 -m sentinel_server sentry --verbose   
sentinel Feb 01 11:16:30 tools.py INFO: naive_bayes.MultinomialNB training records 3001 tagged 114 scope ['eventMessage', 'messageType', 'category']
sentinel Feb 01 11:16:30 tools.py INFO: naive_bayes.BernoulliNB training records 3001 tagged 114 scope ['eventMessage', 'messageType', 'category']
```    

We can keep adjusting our model until we no longer occur these types of occurrences.  In this training session, I added 5 more occurrences that I deemed false-positives.    
Tagging all five new entries as '0', the model now has a training set of 3006 total records with 114 tagged as '1'.    
```
python3.8 -m sentinel_server sentry --verbose   
sentinel Feb 01 11:20:56 tools.py INFO: naive_bayes.MultinomialNB training records 3006 tagged 114 scope ['eventMessage', 'messageType', 'category']
sentinel Feb 01 11:20:57 tools.py INFO: naive_bayes.BernoulliNB training records 3006 tagged 114 scope ['eventMessage', 'messageType', 'category']
```

Continuing to run the program will encounter various occurrences that may or may not be correct predictions.    
```
sentinel list-occurrence    
```
Syslog data has many reoccurring patterns and frequencies, as well as single outlier occurrences or events.    
Using the "bag of words" approach for text analysis on syslog data does appear to work well.    

---

An interesting observation;   
While training my model sets on syslog data,     
I have found that the naive_bayes BernoulliNB has less false-positives than MultinomialNB,    
which is interesting to me since naive_bayes MultinomialNB is the ?common?/*popular* text classification algorithm.    

---


TODO: 
  auto prune occurrence table? 
  put occurrence in mem (not sql)
  make auto tagger
  auto reload on model update



