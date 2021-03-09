


sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"error","data":["eventMessage","messageType","category"],"not":["NoError"]}'

sentinel update-rule watch-syslog-rule-2 '{"config":"watch-syslog","search":"Error","ignorecase":"False","data":["eventMessage","messageType","category"],"not":["NoError"],"pass":["952ac1cce6fe8b80d9f75f3718bc1943ddb63241","7282d72d7518628bcc9cc643fd663bd20ec0a112"]}'



#Mac
sentinel logstream
sentinel update-config watch-syslog '{"logfile":"stream","rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'

sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"error","data":["eventMessage","messageType","category"]}'



#Linux
sentinel logstream
sentinel update-config watch-syslog '{"logfile":"stream","rules":["MESSAGE","SYSLOG_IDENTIFIER","SYSLOG_FACILITY","PRIORITY","USER_UNIT","_TRANSPORT","_CMDLINE","_COMM","_EXE","_HOSTNAME"]}'
sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"error","data":["MESSAGE","SYSLOG_IDENTIFIER","_CMDLINE"]}'

----

sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"error","data":["eventMessage","messageType","category"]}'


('watch-syslog-rule-1', '2021-01-26 22:40:55', '{"config":"watch-syslog","search":"error","data":["eventMessage"],"not":["noerror","XPC_ERROR_CONNECTION_INVALID","com.apple.Maps.MapsSync.store"]}')
('watch-syslog-rule-2', '2021-01-22 23:30:01', '{"config":"watch-syslog","search":"hello","data":["eventMessage"]}')







xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


WORKING-ON:

sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"error","data":"MESSAGE"}'
CHANGE TO:
sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"error","data":["MESSAGE","SYSLOG_IDENTIFIER","_CMDLINE"]}'


# Sentinel watch-syslog using expert rules

## Linux syslog

### distributed sparse logging


```
sentinel update-config watch-syslog '{"logfile":"stream","rules":["MESSAGE","SYSLOG_IDENTIFIER","SYSLOG_FACILITY","PRIORITY","USER_UNIT","_TRANSPORT","_CMDLINE","_COMM","_EXE","_HOSTNAME"]}'
```

```
sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":"error","data":"MESSAGE"}'
```
```
sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","match":[{"SYSLOG_IDENTIFIER":"systemd-logind"},{"_COMM":"systemd-logind"},{"_EXE":"/lib/systemd/systemd-logind"},{"_CMDLINE":"/lib/systemd/systemd-logind"}]}'
```


#
#mac has
#"messageType":"Error"

sentinel update-rule watch-syslog-rule-11 '{"config":"watch-syslog","match":[{"messageType":"Error"}]}'




