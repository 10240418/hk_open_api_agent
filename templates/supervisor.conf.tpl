[program:{{ project_name }}]
command=/home/admin/{{ project_name }}/run.sh
directory=/home/admin/{{ project_name }}
user=admin
autostart=true
autorestart=true
startsecs=3
stdout_logfile=/home/admin/{{ project_name }}/tmp/supervisor-stdout.log
stderr_logfile=/home/admin/{{ project_name }}/tmp/supervisor-stderr.log
