
sentinel check-ntp

sentinel update-job ntp-check '{"repeat": "24hour", "job": "ntp-check"}'


