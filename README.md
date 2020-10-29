# sentinel  


A Python program for the automation of mundane security tasks.  

   ...that has become a security plugin for prometheus   

---  

noun.  a soldier or guard whose job is to stand and keep watch.  

---  

seriously, what is it?  

for me, its a command line tool for scanning networks via nmap and collecting the output for pci and soc2 audits.    
since, it has evolved and integrated into prometheus   https://prometheus.io/     
sentry mode is simply a daemon that runs as a service,  
and outputs prometheus data structures that can be consumed by prometheus.   
which has since helped in achieving compliance.   


---   

Remote  
- Network Discovery  
- Port Scanner  
- Vulnerability Scanner  

Local  
- Listening Ports and Services  
- Established Connections  
- File Integrity Monitoring
- Git File Integrigy //IN-PROGRESS     
- Snort Integration  //TODO        
- Virus Scanner //TODO (clam-av)      
  
---

Relies on command line tools nmap, netstat, ping, arp, lsof, nslookup.  

```
sentinel --help   
```

