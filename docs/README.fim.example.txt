  
# example usage; create file integrity check the checks every 12 hours and sends an alert notice    
  
# list fims    
```  
./sentinel.py list-fims    
```    
  
# create empty fim    
```    
./sentinel.py update-fim fim-1 '{}'    
```    
  
# add fils to the fim    
```    
./sentinel.py add-fim fim-1 /etc/hosts    
./sentinel.py add-fim fim-1 /etc/passwd    
```    
  
```    
./sentinel.py list-fims                  
(1, 'fim-1', '2020-09-29 21:45:48', '{"/etc/hosts": "", "/etc/passwd": ""}')  
```  
  
# create checksum (b2sum)  
```  
./sentinel.py b2sum-fim fim-1  
{'/etc/hosts': '', '/etc/passwd': ''}  
/etc/hosts 914a082d755db5ec57e80315741fa06c6b3cf281  
/etc/passwd 14e6089b58703286399d670073a758014064c41a  
```  
  
# check if checksum has changed  
```  
./sentinel.py check-fim fim-1  
```  
  
---  
  
# add a job that re-checks every 12 hours  
Specifically, the "fim-check" job gets its config data from the 'list-fims', such as "fim-1" created earlier  
```  
./sentinel.py update-job fim-job-1 '{"repeat":"12hour", "job":"fim-check", "config":"fim-1"}'  
```  
  
Once a job has run via the job runner, it updates the reports table as well as its job status start, done, success  
```  
./sentinel.py list-jobs  
```  
```  
./sentinel.py list-reports  
```  
  
```  
% ./sentinel.py list-jobs          
(2, 'fim-job-1', '2020-09-29 22:03:29', '{"repeat": "12hour", "job": "fim-check", "config": "fim-1", "start": "2020-09-29 15:03:29", "done": "2020-09-29 15:03:29", "success": true}')  
% ./sentinel.py list-reports       
(1, 'fim-1', '2020-09-29 22:03:29', '{}')  
```  
  
Thus, the reports table will populate with any detected changes...    
```  
./sentinel.py list-fims-changed  
/etc/hosts CHANGED  
```  
The reports table has,    
```  
% ./sentinel.py list-reports    
(2, 'fim-1', '2020-09-29 22:13:03', '{"/etc/hosts": "CHANGED"}')  
```  
  
---  
  
  
Create an alert for list-reports 'fim-1'


```
./sentinel.py list-alerts
``` 
  
  
```  
./sentinel.py update-alert alert-on-fim-1 '{"report":"fim-1", "config":"logfile"}'
  
``` 


manually run the alert,
```
./sentinel.py run-alert alert-on-fim-1
```


And this is where i'm at... so, back to programming the nex steps...



  
  
  
  
  
