
#sentinel update-job vuln-scan-1 '{"time": "2020-09-20 00:00:00", "job": "vuln-scan", "ips": ["192.168.0.159"]}'
#sentinel update-job net-watch-1 '{"repeat": "5min", "job": "net-watch", "ips": ["192.168.0.1/24"]}'

sentinel update-job net-scan-1 '{"repeat": "5min", "job": "net-scan", "ips": ["192.168.0.1/24"]}'

sentinel update-job net-scan-1 '{"repeat": "1min", "job": "net-scan", "ips": ["192.168.0.1/24"]}'

sentinel update-job net-scan-1 '{"repeat": "3min", "job": "net-scan", "ips": ["192.168.0.0/24"]}'

