

#[Privacy] Did stop advertising with error: (null)
sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":[{"eventMessage":"error"}],"not":["NoError","[Privacy] Did stop advertising with error: (null)"]}'




#Linux......................................................

sentinel update-config watch-syslog '{"logfile":"stream"}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","match":[{"SYSLOG_IDENTIFIER":"sudo"},{"PRIORITY":"5"}],"not":[{"MESSAGE":"open /etc/securetty: No such file or directory"}]}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","search":[{"MESSAGE":"error"}],"not":["NoError"]}'



#MAC........................................................

sentinel update-config watch-syslog '{"logfile":"stream"}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":[{"eventMessage":"error"}],"not":["NoError"],"pass":["952ac1cce6fe8b80d9f75f3718bc1943ddb63241","7282d72d7518628bcc9cc643fd663bd20ec0a112"]}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":[{"eventMessage":"error"}],"not":["NoError"]}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","search":[{"eventMessage":"fault"}],"not":["default"]}'

sentinel update-rule watch-syslog-3 '{"config":"watch-syslog","match":[{"subsystem":"com.apple.mdns"},{"category":"resolver"}],"not":[{"eventMessage":"NoError"}]}'

sentinel update-rule watch-syslog-4 '{"config":"watch-syslog","match":[{"subsystem":"com.apple.locationd.Position"},{"category":"GeneralCLX"}]}'

sentinel update-rule watch-syslog-5 '{"config":"watch-syslog","match":[{"subsystem":"com.apple.apsd"},{"category":"connection"}]}'

sentinel update-rule watch-syslog-6 '{"config":"not-watch-syslog","what":[{"broken":"broken"}]}'

sentinel update-rule watch-syslog-7 '{"config":"watch-syslog","match":[{"category":"connection"}]}'


#################################################################################################################################################################################








#MAC........................................................

sentinel update-config watch-syslog '{"logfile":"stream"}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","data":["eventMessage"],"contains":["error"],"not":["NoError"]}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","data":["eventMessage"],"contains":["fault"],"not":["default"]}'

sentinel update-rule watch-syslog-3 '{"config":"watch-syslog","data":["senderImagePath"],"equals":["/usr/sbin/mDNSResponder"]}'


search|match







sentinel update-config watch-syslog '{"logfile":"stream"}'

sentinel update-rule watch-syslog-3 '{"config":"watch-syslog","senderImagePath":"/usr/sbin/mDNSResponder","eventMessage":["eventMessage"],"except":["NoError"]}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","eventMessage":"eventMessage","match":["eventMessage"],"except":["NoError"]}'

sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","search":["fault"],"data":["eventMessage"],"except":["default"]}'


---

sentinel update-config watch-syslog '{"logfile":"stream"}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":["error"],"data":["eventMessage"],"except":["NoError"]}'
sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","search":["fault"],"data":["eventMessage"],"except":["default"]}'


---

sentinel update-config watch-syslog '{"logfile":"stream"}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":["error","fault"],"data":["eventMessage"]}'

sentinel update-rule watch-syslog-1 '{"config":"watch-syslog","search":["error","fault"],"data":["eventMessage"],"except":["NoError"]}'
sentinel update-rule watch-syslog-2 '{"config":"watch-syslog","search":["error"],"data":["eventMessage"],"ignore":["category":"resolver"]}'

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



