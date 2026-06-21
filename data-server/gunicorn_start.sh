#!/bin/bash
cd /root/course-project/data-server
exec gunicorn \
    --workers 1 \
    --bind 0.0.0.0:5000 \
    --access-logfile /var/log/flask-access.log \
    --error-logfile /var/log/flask-error.log \
    --timeout 300 \
    --max-requests 200 \
    --max-requests-jitter 50 \
    wsgi:app
