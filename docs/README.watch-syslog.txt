
# mac
sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules","naive_bayes"],"keys":["eventMessage","eventType","messageType","activityIdentifier","subsystem","category","processImagePath","senderImagePath","source","processID","parentActivityIdentifier"]}'

# linux
sentinel update-config watch-syslog '{"logfile":"stream","engine":["rules","naive_bayes"],"keys":["MESSAGE","SYSLOG_IDENTIFIER","SYSLOG_FACILITY","PRIORITY","USER_UNIT","_TRANSPORT","_CMDLINE","_COMM","_EXE","_SELINUX_CONTEXT","_HOSTNAME","_PID","_UID","_GID"]}'

#---


sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","match":[{"SYSLOG_IDENTIFIER":"sudo"}]}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","match":[{"subsystem":"com.apple.apsd"},{"category":"connection"}]}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","match":[{"processImagePath":"\/usr\/bin\/sudo"},{"eventType":"logEvent"}]}'




