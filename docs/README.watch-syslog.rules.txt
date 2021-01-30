
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




