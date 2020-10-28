# sentinel  

noun.  a soldier or guard whose job is to stand and keep watch.  

Python program for the automation of mundane security tasks.  Relies on command line tools nmap, netstat, ping, arp, nslookup.  

---  

IN-PROGRESS  

prometheus integration  

```
./sentinel.py update-config prometheus '{"port": 9111, "path": "/metrics"}'    
```


---  

Remote  
- Network Discovery  
- Port Scanner  
- Vulnerability Scanner  

Local  
- Listening Ports and Services  
- Established Connections  
- File Integrity Monitoring  
- Virus Scanner //TODO (clam-av)  

---

```
./sentinel.py [option]

./sentinel.py --help   

    options:

        nmap-net net
        ping-net ip/net

        port-scan [ip/net] [level]
        list-nmaps
        nmap ip [level]
        del-nmap ip
        clear-nmaps

        vuln-scan [ip/net]
        list-vulns [id]
        del-vuln id
        clear-vulns
        check-vuln id
        email-vuln id

        detect-scan-net [ip/net]
        detect-scan ip
        list-detects [id]
        del-detect id
        clear-detects

        arps
        manuf mac
        lsof port
        rdns ip [srv]
        myip

        udp ip port
        udpscan ip port
        tcp ip port

        list-macs
        update-manuf mac
        update-dns mac ip

        listening
        listening-detailed
        listening-details port
        listening-allowed
        listening-alerts
        listening-allow port
        listening-remove port

        established
        established-rules
        established-rules-filter
        established-rule ALLOW|DENY proto laddr lport faddr fport
        established-alerts

        list-ips
        update-ip ip data
        update-ip-item ip item value
        delete-ip-item ip item value
        del-ip ip
        clear-ips

        list-jobs
        list-jobs-running
        list-jobs-available
        run-job name
        update-job name data
        delete-job name
        clear-jobs

        list-configs
        update-config name data
        delete-config id

        list-reports
        delete-report id

        list-alerts
        delete-alert id
        run-alert name
        update-alert name data
        run-alert name
        clear-alerts

        list-fims
        list-fims-changed
        check-fim [name]
        b2sum-fim [name]
        b2sum /dir/file
        update-fim name data
        delete-fim id
        add-fim name /dir/file
        del-fim name /dir/file

        sentry

        ---

        list-counts
        run-create-db
        run-ps


