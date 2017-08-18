from celery import Celery
from flask_log_request_id.extras.celery import configure_celery

celery = Celery()
configure_celery(celery)
