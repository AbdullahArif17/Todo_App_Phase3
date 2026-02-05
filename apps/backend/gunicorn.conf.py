"""
Gunicorn configuration for Todo AI Backend production deployment
"""
import os
import multiprocessing

# Server socket
bind = "0.0.0.0:7860"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 300
keepalive = 5

# Restart settings
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "todo_ai_backend"

# Security and performance
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Timeout for graceful shutdown
graceful_timeout = 30