
# list fims
sentinel list-fims

# create new fim
sentinel update-fim fim-1 '{}' 

# add files to fim-1
sentinel add-fim fim-1 /etc/hosts   
sentinel add-fim fim-1 /etc/passwd   
sentinel add-fim fim-1 /etc/shadow
sentinel add-fim fim-1 /etc/sudoers
sentinel add-fim fim-1 /etc/group
  
# run initial checksum
sentinel b2sum-fim fim-1

# manually run check
sentinel check-fim fim-1

# set a job to check automatically
sentinel update-job fim-job-1 '{"repeat":"12hour", "job":"fim-check", "config":"fim-1"}'

#list/view sentinel sentry prom output
sentinel list-proms

should look something like,
```
sentinel_job{repeat="12hour",job="fim-check",config="fim-1",start="2020-12-29 18:55:10",name="fim-job-1",done="2020-12-29 18:55:10",success="True"} 1
sentinel_job_output{config="fim-1",job="fim-job-1",done="2020-12-29 18:55:10"} 0
```
 
