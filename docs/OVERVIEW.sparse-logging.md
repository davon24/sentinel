
Sentinel - Distributed Systems Sparse Logging (Expert Rules with SysLog Data)

Provides a view of multiple logging systems without centralized or aggregated syslog data.  By leveraging Prometheus.io monitoring and alerting toolkit, expert rules can be applied in a sparse manner to search and identify domain specific knowledge and data.

Syslog Data.
SysLog (System Logging) data accumulates and consumes storage.  Configuring sparse logging is a mechanism that enables logging and alerting at the host without the need to save or aggregate system logs.  Sentinel logstream is a process that attaches to the system's syslog facility as JSON data.  Each line of syslog data is then passed through the rule engine.

Prometheus integration.
All data is presented in prometheus format.  Expert Rules that yield a result are consumed (scraped) by prometheus.  Prometheus alerts can be constructed on these yield results.  Alert conditions are defined and managed by the prometheus ecosystem.            

Expert Rules Engine.
Syslog data is in JSON format.  The scope of the data are the key value pairs of the JSON object.  Rules can be constructed to search and match conditions based on keys, values, and/or pairs.  

Domain knowledge.
Domain specific knowledge is necessary.  For example, a Linux system configuration might look like:
```
sentinel update-config watch-syslog '{"config":"logstream","logfile":"stream","rules":["MESSAGE","SYSLOG_IDENTIFIER","PRIORITY","_CMDLINE","_EXE"]}'

sentinel update-rule rule-1 '{"config":"watch-syslog","search":"Call Trace","ignorecase":"False","data":["MESSAGE"]}'
sentinel update-rule rule-2 '{"config":"watch-syslog","search":"Out of memory","ignorecase":"False","data":["MESSAGE"]}'
sentinel update-rule rule-3 '{"config":"watch-syslog","search":"Killed process","ignorecase":"False","data":["MESSAGE"]}'
sentinel update-rule rule-4 '{"config":"watch-syslog","search":"error","data":["MESSAGE"],"not":["xfs collector failed","jmx_exporter.rules"],"pass":["1afce5868d6ca4f309be5c77fd05b6d13509c244"]}'
sentinel update-rule rule-5 '{"config":"watch-syslog","match":[{"SYSLOG_IDENTIFIER":"sudo"},{"PRIORITY":"5"}]}'
sentinel update-rule rule-6 '{"config":"watch-syslog","match":[{"SYSLOG_IDENTIFIER":"su"},{"PRIORITY":"5"}]}'

```  

Fingerprint data.
The scope data maintains a cryptographic BLAKE2 hash (fingerprint) each data.  This allows the Expert Rules Engine to identify reoccurring and repetitive data patterns.  The scope data should not contain continuously changing data such as time stamps or incrementing values.  Otherwise, the fingerprint will be continuously changing and different each time.  
         
        
- Logging and alerting for isolated, PCI, and multi-layered SOC2 environments.

---

Distributed Systems
https://en.wikipedia.org/wiki/Distributed_computing

Prometheus.io
https://en.wikipedia.org/wiki/Prometheus_(software)

Rule-base System
https://en.wikipedia.org/wiki/Rule-based_system

Sparse
thinly dispersed or scattered

Syslog
https://en.wikipedia.org/wiki/Syslog

JSON
https://en.wikipedia.org/wiki/JSON

Fingerprint data
https://en.wikipedia.org/wiki/Fingerprint_(computing)




