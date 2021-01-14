
sentinel update-job established-check-1 '{"repeat": "5min", "job": "established-check"}'

sentinel update-job proc-monitor '{"repeat": "5min", "job": "ps-check"}' 

sentinel update-fim fim-1 '{}'
sentinel add-fim fim-1 /etc/hosts   
sentinel add-fim fim-1 /etc/passwd   
sentinel add-fim fim-1 /etc/shadow
sentinel add-fim fim-1 /etc/sudoers
sentinel add-fim fim-1 /etc/group

sentinel b2sum-fim fim-1

sentinel update-job fim-job-1 '{"repeat":"12hour", "job":"fim-check", "config":"fim-1"}'

