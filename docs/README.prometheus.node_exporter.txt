

./node_exporter --collector.textfile.directory=/opt/sentinel/python/db

curl localhost:9100/metrics


# HELP sentinel_job Metric read from /opt/sentinel/python/db/sentinel.db.prom
# TYPE sentinel_job untyped
sentinel_job{config="",done="2020-10-14 21:14:58",job="ps-check",name="proc-monitor",repeat="1min",start="2020-10-14 21:14:58",success="True"} 1
sentinel_job{config="",done="2020-10-14 21:15:22",job="established-check",name="established-check-1",repeat="1min",start="2020-10-14 21:15:22",success="True"} 1
sentinel_job{config="fim-1",done="2020-10-14 21:15:22",job="fim-check",name="fim-job-1",repeat="1min",start="2020-10-14 21:15:22",success="True"} 1
sentinel_job{config="fim-2",done="2020-10-14 21:15:22",job="fim-check",name="fim-job-2",repeat="1min",start="2020-10-14 21:15:22",success="True"} 1
# HELP sentinel_job_output Metric read from /opt/sentinel/python/db/sentinel.db.prom
# TYPE sentinel_job_output untyped
sentinel_job_output{added1="",added2="",changed1="",config="",defunct="",done="2020-10-14 21:15:22",faddr="17.57.144.116",fport="5223",job="established-check",laddr="192.168.2.24",lport="60542",name="established-check-1",procs="",proto="tcp4"} 1
sentinel_job_output{added1="",added2="",changed1="",config="",defunct="0",done="",faddr="",fport="",job="proc-monitor",laddr="",lport="",name="",procs="453",proto=""} 1
sentinel_job_output{added1="",added2="",changed1="",config="fim-2",defunct="",done="2020-10-14 21:15:22",faddr="",fport="",job="fim-job-2",laddr="",lport="",name="",procs="",proto=""} 0
sentinel_job_output{added1="/etc/bashrc",added2="/etc/profile",changed1="/etc/hosts",config="fim-1",defunct="",done="2020-10-14 21:15:22",faddr="",fport="",job="fim-job-1",laddr="",lport="",name="",procs="",proto=""} 3
# HELP sentinel_process Metric read from /opt/sentinel/python/db/sentinel.db.prom
# TYPE sentinel_process untyped
sentinel_process 2
# HELP sentinel_threads Metric read from /opt/sentinel/python/db/sentinel.db.prom
# TYPE sentinel_threads untyped
sentinel_threads 4
# HELP sentinel_up Metric read from /opt/sentinel/python/db/sentinel.db.prom
# TYPE sentinel_up untyped
sentinel_up 1



