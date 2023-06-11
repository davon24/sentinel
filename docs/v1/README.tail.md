

sentinel update-config watch-syslog '{"config":"tail","logfile":"/var/log/messages","rules":["MESSAGE","SYSLOG_IDENTIFIER","PRIORITY","_CMDLINE","_EXE"]}'


