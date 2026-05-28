server {
    listen {{ port }};
    server_name _;
    root /home/admin/{{ project_name }}/dist;
    location / { try_files $uri $uri/ /index.html; }
}
