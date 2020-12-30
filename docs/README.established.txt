
# show established
sentinel established

# and show established rules
sentinel established-rules

# and show the current alerts
sentinel established-alerts

---

# set a job that checks every 5min
sentinel update-job established-check-1 '{"repeat": "5min", "job": "established-check"}'

# create an allow rule for localhost...
sentinel established-rule ALLOW tcp 127.0.0.1 '*' 127.0.0.1 '*'

# view job output
sentinel list-jobs

# view prom output
sentinel list-proms

```
sentinel_job_output{name="established-check-1",sentinel_job="established-check",proto="tcp",laddr="10.0.1.128",lport="22",faddr="166.171.122.77",fport="42491",prog="sshd",user="root",prog2="sshd",user2="root",prog3="sshd",user3="root",prog4="sshd",user4="karl.rink",prog5="sshd",user5="root",prog6="sshd",user6="karl.rink",prog7="sshd",user7="root",prog8="sshd",user8="sshd",done="2020-12-29 19:10:41"} 1
```

