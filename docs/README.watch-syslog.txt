
sentinel update-config watch-syslog '{"logfile":"stream"}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":["error","fault"],"data":"eventMessage","except"....}'




sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","search":["error","fault"],"key":"eventMessage"}'


---



sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","except":[{"category":"default"}]}'

sentinel list-rules
sentinel delete-rule name

---

sentinel update-config watch-syslog '{"logfile":"stream","search":["error","fault"]}'

sentinel update-config watch-syslog '{"logfile":"stream","search":[]}'

sentinel update-config watch-syslog '{"logfile":"stream"}'

---

sentinel update-config watch-syslog '{"logfile":"stream","format":"json"}'

---


log stream mac

journalctl linux



