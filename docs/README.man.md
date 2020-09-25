
# sentinel

noun.  a soldier or guard whose job is to stand and keep watch.

---

Python program for the automation of mundane security tasks.  Relies on command line tools nmap, netstat, ping, arp, nslookup, lsof

---

# Running Sentinel as a Service (Sentry Mode)
```
./sentinel.py sentry
```
You can setup and run sentinel as a service.  `Sentry Mode` is sentinel running as a daemon.  This is useful for scheduling jobs, and allowing non-privilged users to run privileged jobs.  Certain commands such as "lsof -i TCP:631" and "nmap -sU" require elevated privileges running as root or Administrator.  The job scheduler provides the ability to submit jobs to the sentinel daemon. And if sentinel is running as root, the job is run with such privileges.  Yes, it is possible to setup and configure the nmap command to run without root privileges. But, and still, I have found this setup a more useful solution.


## Setup sentinel as a service MacOS X
```
sudo cp sentry.sentinel.plist /Library/LaunchDaemons/
sudo launchctl load -w /Library/LaunchDaemons/sentry.sentinel.plist
```

## Setup sentinel as a service Linux
```
sudo cp linux.sentinel.service /lib/systemd/system/sentinel.service
sudo systemctl enable sentinel
sudo systemctl start sentinel
```

---


# Jobs and the Job Scheduler

- job name can be anything
- date format "2020-09-20 00:00:00"

time and repeat

## Jobs

 - vuln-scan
 - port-scan
 - port-scan2

Some quick job examples...
```
# vuln-scan single host.  it will run the job immediatly if the "time" is set to the past.
./sentinel.py update-job vuln-scan-1 '{"time": "2020-09-20 00:00:00", "job": "vuln-scan", "ips": ["192.168.0.81"]}'

# port-scan a subnet.  This will auto-discovery hosts on the network and port scan each host discovered. this will run in the year 2021
./sentinel.py update-job port-scan-level2 '{"time": "2021-09-20 13:00:00", "job": "port-scan2", "ips": ["192.168.0.1/24"]}'

# vuln-scan two hosts.  run the job every 5 minutes.
./sentinel.py update-job vuln-scan-2 '{"repeat": "5min", "job": "vuln-scan", "ips": ["192.168.0.1", "192.168.0.2"]}'



```


---

# Local

## Listening Ports and Services

## Established connections

## FIM

## Virus Scanner

---

# Remote

Network discovery, port scanner, vulnerability scanner, and detection are all 'nmap' commands.  Ensure you have the latest version of nmap installed.  https://nmap.org/    

## Network Discovery
```
./sentinel.py nmap-net 192.168.0.1/24
```
nmap-net is using the open source tool nmap      https://nmap.org/     
cmd = 'nmap -n -sn ' + net     
-n (No DNS resolution)    
-sn (Ping Scan - disable port scan)    
The default host discovery done with -sn consists of an ICMP echo request, TCP SYN to port 443, TCP ACK to port 80, and an ICMP timestamp request by default. [man nmap]


## Port Scanner
```
./sentinel.py port-scan 192.168.0.1
```
cmd = 'nmap -n -F -T5 ' + ip   
Nmap scans the most common 1,000 ports for each scanned protocol. With `-F`, this is reduced to 100.       
-F (Fast mode - Scan fewer ports than the default scan)    
-T5 (max-retries 2, max-rtt-timeout 300)    

Advanced port scanning requires root privileges.  Running nmap as an unprivileged user is possible but requires additional setup.  Because of this, I have organized the port scanner with level options.

level 1 - tcp only, top 100 ports    
level 2 - requires root, tcp+udp, top 1000 ports    
level 3 - requires root, tcp+udp, 1-65535 ports    

**`--top-ports`**    
While more than a hundred thousand (total) TCP and UDP ports exist, the vast majority of open ports fall within a much smaller set. According to our research, the top 10 TCP ports and top 1,075 UDP ports represent half of the open ports for their protocol. To catch 90% of the open ports, you need to scan 576 TCP ports and 11,307 UDP ports. By default, Nmap scans the top 1,000 ports for each scan protocol requested. This catches roughly 93% of the TCP ports and 49% of the UDP ports. [man nmap]     
```
port-scan [ip/net] [level]
```
 ```
 sudo ./sentinel.py port-scan 192.168.0.1/24 2
 ```


## Vulnerability Scanner
```
./sentinel.py vuln-scan 192.168.0.1
```
This is a specialized nmap command that engages Nmap Scripting Engine (NSE).  
cmd = 'nmap -Pn --script=vuln ' + ip

The Nmap Scripting Engine (NSE) is one of Nmap's most powerful and flexible features. It allows users to write (and share) simple scripts (using the Lua programming language) to automate a wide variety of networking tasks.  Each script contains a field associating it with one or more categories. Currently defined categories are auth, broadcast, default.  discovery, dos, exploit, external, fuzzer, intrusive, malware, safe, version, and vuln. These are all described at https://nmap.org/book/nse-usage.html#nse-categories [man nmap]    

## OS and Service Version Detection
```
./sentinel.py detect-scan 192.168.0.1
```
cmd = 'nmap -n -O -sV ' + ip    
-O (Enable OS detection)    
-sV (Probe open ports to determine service/version info)    
This command requires root privileges.     

---

# Example vuln-scan three hosts   

We'll scan 3 hosts for vulnerabilities.     
```
./sentinel.py vuln-scan 192.168.2.1
./sentinel.py vuln-scan 192.168.0.184
./sentinel.py vuln-scan 192.168.0.1
```
Once a scan has finished, the output is saved to the sentinel database.  You can list the scans with the option `list-vulns`      
```
./sentinel.py list-vulns 
3 192.168.0.1 2020-09-18 05:43:40 8443/tcp
2 192.168.0.184 2020-09-17 02:28:20 80/tcp,443/tcp,8873/tcp,22939/tcp
1 192.168.2.1 2020-09-17 01:51:59 -
``` 
In the above list-vulns we have one negative and two hosts with vulnerabilities.  The scan with id `3` has a vulnerability on `8443/tcp` , while scan id `1` is negative.  To view the details of the host with scan id `2` we can issue the following command:    
```
./sentinel.py list-vulns 2
2 192.168.0.184 2020-09-17 02:28:20 80/tcp,443/tcp,8873/tcp,22939/tcp
Starting Nmap 7.80 ( https://nmap.org ) at 2020-09-16 19:25 PDT
Pre-scan script results:
| broadcast-avahi-dos: 
|   Discovered hosts:
|     224.0.0.251
|   After NULL UDP avahi packet DoS (CVE-2011-1002).
|_  Hosts are all up (not vulnerable).
Nmap scan report for 192.168.0.184
Host is up (0.036s latency).
Not shown: 994 closed ports
PORT      STATE SERVICE
80/tcp    open  http
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|_  /proxy/: Potentially interesting folder
|_http-passwd: ERROR: Script execution failed (use -d to debug)
| http-slowloris-check: 
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|       
|     Disclosure date: 2009-09-17
|     References:
|       http://ha.ckers.org/slowloris/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
443/tcp   open  https
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-passwd: ERROR: Script execution failed (use -d to debug)
| http-slowloris-check: 
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|       
|     Disclosure date: 2009-09-17
|     References:
|       http://ha.ckers.org/slowloris/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_ssl-ccs-injection: No reply from server (TIMEOUT)
| ssl-dh-params: 
|   VULNERABLE:
|   Diffie-Hellman Key Exchange Insufficient Group Strength
|     State: VULNERABLE
|       Transport Layer Security (TLS) services that use Diffie-Hellman groups
|       of insufficient strength, especially those using one of a few commonly
|       shared groups, may be susceptible to passive eavesdropping attacks.
|     Check results:
|       WEAK DH GROUP 1
|             Cipher Suite: TLS_DHE_RSA_WITH_DES_CBC_SHA
|             Modulus Type: Non-safe prime
|             Modulus Source: RFC5114/1024-bit DSA group with 160-bit prime order subgroup
|             Modulus Length: 1024
|             Generator Length: 1024
|             Public Key Length: 1024
|     References:
|_      https://weakdh.org
|_sslv2-drown: 
548/tcp   open  afp
873/tcp   open  rsync
8873/tcp  open  dxspider
| ssl-dh-params: 
|   VULNERABLE:
|   Anonymous Diffie-Hellman Key Exchange MitM Vulnerability
|     State: VULNERABLE
|       Transport Layer Security (TLS) services that use anonymous
|       Diffie-Hellman key exchange only provide protection against passive
|       eavesdropping, and are vulnerable to active man-in-the-middle attacks
|       which could completely compromise the confidentiality and integrity
|       of any data exchanged over the resulting session.
|     Check results:
|       ANONYMOUS DH GROUP 1
|             Cipher Suite: TLS_DH_anon_WITH_AES_256_CBC_SHA
|             Modulus Type: Safe prime
|             Modulus Source: Unknown/Custom-generated
|             Modulus Length: 512
|             Generator Length: 8
|             Public Key Length: 512
|     References:
|_      https://www.ietf.org/rfc/rfc2246.txt
|_sslv2-drown: 
22939/tcp open  unknown
| ssl-dh-params: 
|   VULNERABLE:
|   Anonymous Diffie-Hellman Key Exchange MitM Vulnerability
|     State: VULNERABLE
|       Transport Layer Security (TLS) services that use anonymous
|       Diffie-Hellman key exchange only provide protection against passive
|       eavesdropping, and are vulnerable to active man-in-the-middle attacks
|       which could completely compromise the confidentiality and integrity
|       of any data exchanged over the resulting session.
|     Check results:
|       ANONYMOUS DH GROUP 1
|             Cipher Suite: TLS_DH_anon_WITH_AES_256_CBC_SHA
|             Modulus Type: Safe prime
|             Modulus Source: Unknown/Custom-generated
|             Modulus Length: 512
|             Generator Length: 8
|             Public Key Length: 512
|     References:
|_      https://www.ietf.org/rfc/rfc2246.txt
|_sslv2-drown: 

Nmap done: 1 IP address (1 host up) scanned in 187.29 seconds
```

---

# Email Module
sentinel can be configured to send email.  The following example shows how to configure and use.  Please store configuration as json.  Here is the minimum necessary to enable and get going with the defaults.    
```
./sentinel.py update-config email '{"smtp_to":"root@localhost"}'
```
A full list of options and their defaults,    
```
    smtp_to   = jdata.get('smtp_to', None)
    smtp_from = jdata.get('smtp_from', 'sentinel')
    smtp_host = jdata.get('smtp_host', '127.0.0.1')
    smtp_port = jdata.get('smtp_port', '25')
    smtp_user = jdata.get('smtp_user', None)
    smtp_pass = jdata.get('smtp_pass', None)
```

---

## List Configs
```
./sentinel.py list-configs
(1, 'email', '2020-09-18 06:12:22', '{"smtp_to":"root@localhost"}')
```

## Email a vuln-scan
```
./sentinel.py email-vuln 2
```




