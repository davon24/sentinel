
Linux MESSAGE  
MacOS eventMessage  


```  
sentinel update-config watch-log-1 '{"config":"tail","type":"apache","format":"clf","logfile":"/tmp/apache2.log"}'

sentinel update-config watch-log-2 '{"config":"tail","type":"mysql","format":"custom","logfile":"/tmp/mysql.log"}'

sentinel update-config watch-log-3 '{"config":"logstream","type":"syslog","format":"json","logfile":"stream","scope":["eventMessage"}'
```

```
sentinel update-rule watch-log-apache-rule-1 '{"config":"watch-log-1","search":"error","data":[]}'

sentinel update-rule watch-log-mysql-rule-1 '{"config":"watch-log-2","search":"error","data":[]}'

sentinel update-rule watch-log-logstream-rule-1 '{"config":"watch-log-3","search":"error","data":["eventMessage"]}'
```


