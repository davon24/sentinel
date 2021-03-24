
as of verson 1.6.20-1  

new data structure "expire":"3600" for rules  

you can add this to any rule (Expert_Rule)  

```  
sentinel update-rule rule-X '{"config":"watch-syslog","search":"error","data":["eventMessage"],"expire":"3600"}'  
```  

will auto-expire any rule hit after 3600 (1 hour).  default is expire=864000 for sentinel_watch_syslog_rule_engine  
this auto-expire currently only applies to sentinel_watch_syslog_rule_engine.  all others are already self-managed  

updating a rule is dynamic now... so you can simply update existing rules json key/value with "expire":"3600"  


