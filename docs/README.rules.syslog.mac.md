# expert rules with syslog data    

distributed logging system for syslog    
https://en.wikipedia.org/wiki/Distributed_computing    

using prometheus architecture  
https://en.wikipedia.org/wiki/Prometheus_(software)    

rule-base system used to store and manipulate knowledge to interpret information in a useful way.    
https://en.wikipedia.org/wiki/Rule-based_system    

---

We'll start by setting the watch-syslog rules configuration    
```
sentinel update-config watch-syslog '{"logfile":"stream","rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]}'
```

The scope of the data is ["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]    
which are the keys from the key/value pairs in the logstream.  The logstream data is in json format. 
https://en.wikipedia.org/wiki/JSON    

---


Next, we'll configure an expert rule.  
```
sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"error","data":["eventMessage","messageType","category"]}'
```
The rule searches for the word 'error' through the text data values in ["eventMessage","messageType","category"].   

---

To run the rule, simply run sentinel in sentry (daemon) mode.  There is a verbose mode.    
You should see the following startup output   
```
sentinel sentry --verbose
sentinel Feb 05 14:16:46 tools.py INFO: Sentry Startup
sentinel Feb 05 14:16:46 tools.py INFO: Sentry watch-syslog logstream 
sentinel Feb 05 14:16:46 tools.py INFO: Sentry watch-syslog expert_rules scope ['eventMessage', 'eventType', 'messageType', 'subsystem', 'category', 'processImagePath', 'senderImagePath', 'source']
``` 


Any data that matches a rule is added to the occurrence table.
```
sentinel list-occurrence
```

---

There can be multiple rules.  We'll add a rule to match on exact key/value pairs.
```
sentinel update-rule watch-syslog-rule-2 '{"config":"watch-syslog","match":[{"subsystem":"com.apple.apsd"},{"category":"connection"}]}'
``` 
The rule will match any time my Apple Time Machine backup occurs.

Rules are run in the order displayed, top down.  The names of rules can be anything, I typically choose easy names like 'watch-syslog-rule-1'.
```
sentinel list-rules
('watch-syslog-rule-1', '2021-02-05 19:37:22', '{"config":"watch-syslog","search":"error","data":["eventMessage","messageType","category"]}')
('watch-syslog-rule-2', '2021-02-05 19:37:35', '{"config":"watch-syslog","match":[{"subsystem":"com.apple.apsd"},{"category":"connection"}]}')
```

---

false-positive https://en.wikipedia.org/wiki/False_positives_and_false_negatives    

Rules can be adjusted as necessary.  For example, the first rule matched on the word 'NoError'.  
```
sentinel list-occurrence watch-syslog-rule-1-ff5995bc229777eb269cf20ba58c8c4293d1b376
('watch-syslog-rule-1-ff5995bc229777eb269cf20ba58c8c4293d1b376', 1, '{"traceID":3105639345815556,"eventMessage":"[Q20195] Sent 37-byte query #1 to <IPv4:BBQJCpqH> over UDP via en12\\/14 -- id: 0x2EB9 (11961), flags: 0x0100 (Q\\/Query, RD, NoError), counts: 1\\/0\\/0\\/0, BBthEVNQ IN AAAA?","eventType":"logEvent","source":null,"formatString":"%{public}sSent %zu-byte query #%u to %@ over %{public}s via %{public}s -- %{public,mdns:dnshdr}.*P, %@","activityIdentifier":0,"subsystem":"com.apple.mdns","category":"resolver","threadID":100942,"senderImageUUID":"82D02211-7080-3191-AD5F-6F4A0E807A2B","backtrace":{"frames":[{"imageOffset":448218,"imageUUID":"82D02211-7080-3191-AD5F-6F4A0E807A2B"}]},"bootUUID":"","processImagePath":"\\/usr\\/sbin\\/mDNSResponder","timestamp":"2021-02-05 11:43:22.859569-0800","senderImagePath":"\\/usr\\/sbin\\/mDNSResponder","machTimestamp":10854631418804,"messageType":"Default","processImageUUID":"82D02211-7080-3191-AD5F-6F4A0E807A2B","processID":231,"senderProgramCounter":448218,"parentActivityIdentifier":0,"timezoneName":""}\n')
```


The occurrence is not a false-positive, but it is not what we want.  You can adjust the rule to 'not' match these types of occurrences.  Additionally, we'll make the search case sensitive.
```
sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"Error","ignorecase":"False","data":["eventMessage","messageType","category"],"not":["NoError"]}'
```

---


Unwanted occurrences may persist.
```
sentinel list-occurrence watch-syslog-rule-1-866d144919148df7e27de9e6a0b68f59a994577d
('watch-syslog-rule-1-866d144919148df7e27de9e6a0b68f59a994577d', 46, '{"traceID":434307574041677828,"eventMessage":"cannot open file at line 44580 of [02c344acea]","eventType":"logEvent","source":null,"formatString":"%s","activityIdentifier":0,"subsystem":"com.apple.libsqlite3","category":"logging-persist","threadID":122367,"senderImageUUID":"D7017429-8D46-3ECB-8B70-4625C74918F3","backtrace":{"frames":[{"imageOffset":194442,"imageUUID":"D7017429-8D46-3ECB-8B70-4625C74918F3"}]},"bootUUID":"","processImagePath":"\\/usr\\/libexec\\/taskgated","timestamp":"2021-02-05 12:22:17.349760-0800","senderImagePath":"\\/usr\\/lib\\/libsqlite3.dylib","machTimestamp":13189110605203,"messageType":"Error","processImageUUID":"E38C25EC-5717-3457-9D1E-54BBABE357D2","processID":1175,"senderProgramCounter":194442,"parentActivityIdentifier":0,"timezoneName":""}\n')
```
In this case, occurrence watch-syslog-rule-1-866d144919148df7e27de9e6a0b68f59a994577d has occurred '46' times.     
To eliminate this occurrence, you can simply narrow the search of data by not including 'messageType' in "data":["eventMessage","category"] since it matched on "messageType":"Error".
Additionally you can use the b2sum as a pass token.   
```
sentinel update-rule watch-syslog-rule-1 '{"config":"watch-syslog","search":"Error","ignorecase":"False","data":["eventMessage"],"not":["NoError"],"pass":["866d144919148df7e27de9e6a0b68f59a994577d"]}'
```
---

The b2sum 866d144919148df7e27de9e6a0b68f59a994577d is the cryptographic BLAKE2 hash of the data in the rules configuration "rules":["eventMessage","eventType","messageType","subsystem","category","processImagePath","senderImagePath","source"]   
https://en.wikipedia.org/wiki/BLAKE_(hash_function)    

The b2sum is used to verify if a piece of data has been seen or not, making it the "fingerprint" of the data.   
Note-Warning: that including continuously-changing data such as "timestamp":"2021-02-05 11:43:22.859569-0800" will prevent the b2sum "fingerprint" from ever repeating.    
The b2sum is appended to the rule to form key 'watch-syslog-rule-1-866d144919148df7e27de9e6a0b68f59a994577d'   
https://en.wikipedia.org/wiki/Fingerprint_(computing)    


