

./sentinel.py update-job vuln-scan-1 '{"time": "2020-09-20 00:00:00", "job": "vuln-scan", "ips": ["192.168.0.159"]}'
./sentinel.py update-job vuln-scan-2 '{"repeat": "5min", "job": "vuln-scan", "ips": ["192.168.0.1", "192.168.0.2"]}'

./sentinel.py update-job vuln-scan-1-subnet '{"time": "2020-09-20 00:00:00", "job": "vuln-scan", "ips": ["192.168.0.1/24"]}'




