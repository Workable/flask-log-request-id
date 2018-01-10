from celery import Celery, signals
from flask_log_request_id.extras.celery import enable_request_id_propagation

celery = Celery()

# You need to enable propagation on celery application
enable_request_id_propagation(celery)

