from celery import Celery
from flask_log_request_id.extras.celery import RequestIDAwareTask

celery = Celery(task_cls=RequestIDAwareTask)
