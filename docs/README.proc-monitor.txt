
# list jobs
sentinel list-jobs

# create proc-monitor job
sentinel update-job proc-monitor '{"repeat": "5min", "job": "ps-check"}' 

# view job status
sentinel list-jobs

# view prom output
sentinel list-proms

#```
#sentinel_job{repeat="5min",job="ps-check",start="2020-12-29 19:01:11",name="proc-monitor",done="2020-12-29 19:01:11",success="True"} 1
#sentinel_job_output{procs="146",defunct="0",sentinel_job="proc-monitor"} 1
#```



