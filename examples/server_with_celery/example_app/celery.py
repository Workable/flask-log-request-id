from celery import Celery, signals
from flask_log_request_id.extras.celery import add_request_id_header, RequestIDAwareTask

# Either sublcass all tasks from RequestIDAwareTask
celery = Celery(task_cls=RequestIDAwareTask)

# Or alternatively register the provided signal handler
signals.before_task_publish.connect(add_request_id_header)