
# server

mkdir ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -sha256 -nodes -days 3650 -subj '/CN=localhost'

sentinel update-config api-http-service '{"config": "api_server","port": 8443, "path": "/api", "key": "abc123", "keyfile": "ssl/key.pem", "certfile": "ssl/cert.pem"}'



# server allow client
sentinel delete-api-token 'NjU3MjRiMGMtMzc5Ni0xMWVkLTkzODgtYmUyNWRlMWI1M2Nh' '{}'

# server tell client to run command
sentinel update-api-token "NjU3MjRiMGMtMzc5Ni0xMWVkLTkzODgtYmUyNWRlMWI1M2Nh" '{"command": "uptime"}'

---

# client

sentinel update-job remote-client-1 '{"repeat": "1min", "job": "remote-client","uuid":"65724b0c-3796-11ed-9388-be25de1b53ca", "url":"https://127.0.0.1:8443/api/post"}'

---

sentinel update-job remote-client-1 '{"repeat": "1min", "job": "remote-client","uuid":"65724b0c-3796-11ed-9388-be25de1b53ca", "url":"http://127.0.0.1:8081/api/post"}'

sentinel register-client remote-client-1 "abc123"

sentinel update-job remote-client-2 '{"repeat": "1min", "job": "remote-client","uuid":"65724b0c-3796-11ed-9388-be25de1b53ca", "url":"https://127.0.0.1:8082/api/post"}'

sentinel register-client remote-client-2 "xyz321"



---

# ssl self signed cert

// POST Request
response = requests.post(
    "https://127.0.0.1:8443/api/post", 
    headers=headers, 
    data=payload,
    verify=False  # <---- Added
)

import urllib3
urllib3.disable_warnings()


