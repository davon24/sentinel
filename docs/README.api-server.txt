
# server
sentinel update-config api-http-service '{"config": "api_server","port": 8081, "path": "/api"}'

# server allow client

sentinel delete-api-token 'NjU3MjRiMGMtMzc5Ni0xMWVkLTkzODgtYmUyNWRlMWI1M2Nh' '{}'
sentinel update-api-token "NjU3MjRiMGMtMzc5Ni0xMWVkLTkzODgtYmUyNWRlMWI1M2Nh" '{"command": "uptime"}'



---

# client

sentinel update-config remote-client '{"config":"remote_client", "uuid":"65724b0c-3796-11ed-9388-be25de1b53ca", "url":"http://127.0.0.1:8081/api/post"}'

#sentinel update-job remote-client '{"repeat": "5min", "job": "remote-client"}'
sentinel update-job remote-client '{"repeat": "1min", "job": "remote-client"}'


sentinel update-job proc-monitor '{"repeat": "1min", "job": "ps-check"}'


