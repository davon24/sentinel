
# Sentinel Server

Sentinel is a python program that interacts with the operating system and presents data in [prometheus](https://prometheus.io) format.  When run as a daemon process, users can schedule jobs and interact with the server via python shared_memory and prometheus interface.  

[![Package Version](https://img.shields.io/pypi/v/sentinel-server.svg)](https://pypi.python.org/pypi/sentinel-server/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)


## Install via pip
requires python 3.8 or newer  
```
pip3 install sentinel-server
```
https://pypi.org/project/sentinel-server/    

## Run via src
```
git clone https://gitlab.com/krink/sentinel.git
python3 sentinel/src/sentinel_server/sentinel.py
```

## Server daemon process (sentry mode)
```
python3.8 -m sentinel_server sentry    
```

## Client command   
```
sentinel [option]    
```

```
./sentinel.py --help


    options:

        list-proms

        list-configs
          update-config name data
          delete-config name
          clear-configs

        nmap-net net
        ping-net ip/net
        net-scan net

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

        arps
        manuf mac
        lsof port
        rdns ip [srv]
        myip

        ip-whois ip

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
          established-lsof
          established-rules
          established-rules-filter
          established-rule ALLOW|DENY proto laddr lport faddr fport
          established-alerts
          delete-established-rule rowid
          clear-established-rules

        list-ips
          update-ip ip data
          update-ip-item ip item value
          delete-ip-item ip item value
          del-ip ip
          clear-ips

        list-jobs
          list-jobs-available
          update-job name data
          delete-job name
          clear-jobs

        list-rules
          update-rule name data
          delete-rule name
          clear-rules

        list-reports
          update-report name data
          delete-report name
          clear-reports

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

        list-files
          add-file /dir/file
          del-file /dir/file
        fim-restore /dir/file [/dir/file]
        fim-diff
        clear-files

        file-type /dir/file

        av-scan dir|file
        list-avs

        list-proms-db
          update-prom-db name data
          clear-proms-db

        list-b2sums
          clear-b2sums

        list-counts
          clear-counts

        register-client job_name server_key
        remote-client job_name

        list-api-tokens
          update-api-token token data
          delete-api-token token
          clear-api-tokens

        list-client-commands
          clear-client-commands
          delete-client-command rowid

        base64 <string>

        list-model [id|tags tag]
          update-model tag json
          update-model-tag id tag
          delete-model id
          clear-model

        list-training [id|tags tag]
          update-training tag json
          update-training-tag id tag
          delete-training id
          clear-training

        list-occurrence [name|-eq,-gt,-lt,-ne,-le,-ge num]
          delete-occurrence name
          clear-occurrence

        copy-occurrence name

        sample-logstream count
        # ? mark-training tag
        # ? mark-training-on name

        list-system-profile
          list-system-profile-full
          gen-system-profile
          get-system-profile-name name
          get-system-profile-rowid rowid
          del-system-profile-name name
          del-system-profile-rowid rowid
          clear-system-profile

        diff-system-profile-rowid rowid rowid
        get-system-profile-data rowid data

        tail file
        logstream
        logstream-json
        logstream-keys
        run-create-db
        run-ps

        ---

        sentry [debug|info|warning|error|critical]


        config

                logstream:
                    rules
                    sklearn naive_bayes.MultinomialNB
                            naive_bayes.BernoulliNB
                            neural_network.MLPClassifier
                tail:
                    rules

                api_server
                http_server
                pushgateway


        list-keys
        list-keys-metric
        list-vals
        get-key key
        expire-keys key1 key2 key3...



```

---   

## Docs

[docs](docs/)

---   

Linux package repo hosting https://gitlab.com/_pkg/sentinel  

---

https://prometheus.io/    



