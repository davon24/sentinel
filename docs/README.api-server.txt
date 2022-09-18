
# server
sentinel update-config api-http-service '{"config": "api_server","port": 8081, "path": "/api"}'


# client

sentinel update-api-token "NjU3MjRiMGMtMzc5Ni0xMWVkLTkzODgtYmUyNWRlMWI1M2Nh" '{"entry": "testing"}'

sentinel delete-api-token 'NjU3MjRiMGMtMzc5Ni0xMWVkLTkzODgtYmUyNWRlMWI1M2Nh'


