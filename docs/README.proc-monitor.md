
./sentinel.py update-job proc-monitor '{"repeat":"5min", "job":"ps-check"}'

#./sentinel.py update-job proc-monitor '{"repeat":"5min", "job":"ps-check", "config":"proc-monitor"}'
#  umm, no.  just use config as name here instead


# dumps into reports...
🎃 krink@Karls-MacBook-Pro python % ./sentinel.py list-reports
(7, 'fim-1', '2020-10-02 12:52:01', '{}')
(10, 'proc-monitor', '2020-10-02 13:25:20', '{"procs": 405, "defunct": 0}')


#---


./sentinel.py update-alert proc-monitor-alert '{"report":"proc-monitor", "config": "logfile"}' 

#no proc-monitor report...
#Exception in thread SentryAlertRunner:
#TypeError: the JSON object must be str, bytes or bytearray, not NoneType
# getReport report is <class 'NoneType'> None

🎃 karl.rink@Karl-MacBook-Pro python % ./sentinel.py list-alerts



./sentinel.py update-job proc-monitor '{"repeat": "1min", "job": "ps-check"}' 


#...




runAlert logic...  1st pass, sent = None , just send
runAlert logic...  2nd pass, already sent? yes = pass...

runAlert logic...  2nd pass, already sent? yes = pass || timedelta = re-send


#---

a one shot alert

./sentinel.py update-job proc-monitor '{"repeat": "1min", "job": "ps-check"}'



./sentinel.py update-alert alert-on-proc-monitor '{"report":"proc-monitor", "config":"logfile", "repeat":"5min"}'
./sentinel.py update-alert alert-on-fim-1 '{"report":"fim-1", "config":"logfile", "repeat":"5min"}'

./sentinel.py update-alert broken-1 '{"report":"report-NONE", "config":"logfile", "repeat":"5min"}'
./sentinel.py update-alert broken-2 '{"report":"report-NONE", "config":"logfile-NONE", "repeat":"5min"}'

#oneshot?...
./sentinel.py update-alert alert-on-proc-monitor '{"report":"proc-monitor", "config":"logfile"}'



#-------------------------------------------------------------------------------------------------------------------


#-----------------------
./sentinel.py list-jobs
('proc-monitor', '2020-10-03 23:08:40', '{"repeat": "1min", "job": "ps-check", "start": "2020-10-03 16:08:40", "done": "2020-10-03 16:08:40", "success": true}')


./sentinel.py list-reports
('proc-monitor', '2020-10-03 23:08:40', '{"procs": 426, "defunct": 0}')


./sentinel.py update-alert alert-1 '{"report":"proc-monitor", "job":"ps-check", "config":"logfile", "procs": 300, "defunct": 1, "repeat": "5min"}'


#-----------------------

./sentinel.py list-jobs
('fim-job-1', '2020-10-03 23:10:35', '{"repeat": "1min", "job": "fim-check", "config": "fim-1", "start": "2020-10-03 16:10:35", "done": "2020-10-03 16:10:35", "success": true}')

./sentinel.py list-reports
('fim-1', '2020-10-03 23:11:38', '{}')
('fim-2', '2020-10-03 23:12:17', '{"/etc/group": "ADDED", "/Users/krink/.ssh/config": "ADDED"}')


./sentinel.py update-alert alert-2 '{"report": "fim-1", "job": "fim-check", "config": "logfile"}'








