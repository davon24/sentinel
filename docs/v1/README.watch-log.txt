

sentinel update-config watch-log-1 '{"config":"tail","type":"apache2","format":"verbose-access","logfile":"/tmp/apache2.log","rules":["line"]}'

sentinel update-rule watch-log-apache-rule-1 '{"config":"watch-log-1","search":"error","pass":["abcdefg"]}'

---  

Linux MESSAGE  
MacOS eventMessage  


```  
sentinel update-config watch-log-1 '{"config":"tail","type":"apache","format":"clf","logfile":"/tmp/apache2.log","rules":["line"]}'

sentinel update-config watch-log-2 '{"config":"tail","type":"mysql","format":"custom","logfile":"/tmp/mysql.log","rules":["line"]}'

sentinel update-config watch-log-3 '{"config":"logstream","logfile":"stream","rules":["eventMessage"]}'

sentinel update-config watch-log-4 '{"config":"logstream","logfile":"stream","rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'

sentinel update-config watch-log-5 '{"config":"logstream","logfile":"stream","sklearn":[{"naive_bayes.MultinomialNB":["eventMessage","messageType","category"]},{"naive_bayes.BernoulliNB":["eventMessage","messageType","category"]}]}'

```

```
sentinel update-rule watch-log-apache-rule-1 '{"config":"watch-log-1","search":"error"}'

sentinel update-rule watch-log-mysql-rule-1 '{"config":"watch-log-2","search":"error"}'

sentinel update-rule watch-log-logstream-rule-1 '{"config":"watch-log-3","search":"error","data":["eventMessage"]}'
```


