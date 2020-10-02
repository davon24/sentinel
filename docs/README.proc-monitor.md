
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






