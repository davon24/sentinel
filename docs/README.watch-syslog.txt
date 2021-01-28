

sentinel update-config watch-syslog '{"logfile":"stream","sklearn":[{"naive_bayes.MultinomialNB":["eventMessage"]},{"naive_bayes.BernoulliNB":["eventMessage"]}],"rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'

sentinel update-config watch-syslog '{"logfile":"stream","sklearn":[{"naive_bayes.MultinomialNB":["eventMessage"]},{"naive_bayes.BernoulliNB":["eventMessage"]}]}'



---




sentinel update-config watch-syslog '{"logfile":"stream","sklearn":["naive_bayes.MultinomialNB","naive_bayes.BernoulliNB"],"rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'


sentinel update-config watch-syslog '{"logfile":"stream","rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'



---

sentinel update-config watch-syslog '{"logfile":"stream","naive_bayes_multinomialnb":["eventMessage"],"naive_bayes_bernoullinb":["eventMessage"],"rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'

sentinel update-config watch-syslog '{"logfile":"stream","naive_bayes_multinomialnb":["eventMessage"],"naive_bayes_bernoullinb":["eventMessage"]}'

sentinel update-config watch-syslog '{"logfile":"stream","rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'

#https://en.wikipedia.org/wiki/Naive_Bayes_classifier

#Multinomial naïve Bayes
#https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html
#sklearn.naive_bayes.MultinomialNB(*, alpha=1.0, fit_prior=True, class_prior=None)

#Bernoulli naïve Bayes
https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.BernoulliNB.html
#sklearn.naive_bayes.BernoulliNB(*, alpha=1.0, binarize=0.0, fit_prior=True, class_prior=None)

#Gaussian naïve Bayes
#https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html
#sklearn.naive_bayes.GaussianNB(*, priors=None, var_smoothing=1e-09)



https://scikit-learn.org/stable/modules/naive_bayes.html#naive-bayes
https://developers.google.com/machine-learning/guides/text-classification/step-2-5

https://en.wikipedia.org/wiki/Support-vector_machine



#Semi-supervised parameter estimation





sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules","naive_bayes"],"keys":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'




sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules":{["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"],"naive_bayes":{["eventMessage"]}]}'

sentinel update-config watch-syslog '{"logfile":"stream","engine":["naive_bayes":["eventMessage"]]}'

sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]]}'


---
sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules","naive_bayes"],"keys":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'



sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":"error","data":"eventMessage","not":["noerror","XPC_ERROR_CONNECTION_INVALID","com.apple.Maps.MapsSync.store"]}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":"error","data":"eventMessage","not":["noerror"]}'


sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules","naive_bayes"],"keys":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":"error","data":"eventMessage"}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":"error","data":"eventMessage"}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","match":[{"processImagePath":"\\/usr\\/bin\\/sudo"},{"eventType":"logEvent"}]}'




#----

after literally watching syslog for a while, need/try to eliminate data items that hinder finger print...  ie, processID continually changes...

---

# mac
sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules","naive_bayes"],"keys":["eventMessage","eventType","messageType","activityIdentifier","subsystem","category","processImagePath","senderImagePath","source","processID","parentActivityIdentifier"]}'

# linux
sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules","naive_bayes"],"keys":["MESSAGE","SYSLOG_IDENTIFIER","SYSLOG_FACILITY","PRIORITY","USER_UNIT","_TRANSPORT","_CMDLINE","_COMM","_EXE","_SELINUX_CONTEXT","_HOSTNAME","_PID","_UID","_GID"]}'

#---


sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","match":[{"SYSLOG_IDENTIFIER":"sudo"}]}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","match":[{"subsystem":"com.apple.apsd"},{"category":"connection"}]}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","match":[{"processImagePath":"\/usr\/bin\/sudo"},{"eventType":"logEvent"}]}'




