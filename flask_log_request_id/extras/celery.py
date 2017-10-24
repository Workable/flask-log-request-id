from celery import Task, current_task
import logging as _logging

from ..request_id import current_request_id
from ..ctx_fetcher import ExecutedOutsideContext


_CELERY_X_HEADER = 'x_request_id'
logger = _logging.getLogger(__name__)


class RequestIDAwareTask(Task):
    """
    Task base class that injects request id to task request object with key 'x_request_id'.
    """

    def apply_async(self, *args, **kwargs):
        # Set default value for 'headers' argument
        if 'headers' not in kwargs or kwargs['headers'] is None:
            kwargs['headers'] = {}
        request_id = current_request_id()
        logger.debug("Forwarding request_id '{}' to the task consumer.".format(request_id))
        kwargs['headers'][_CELERY_X_HEADER] = request_id

        return super(RequestIDAwareTask, self).apply_async(*args, **kwargs)

def add_request_id_header(headers=None, **kwargs):
    if _CELERY_X_HEADER not in headers:
        headers[_CELERY_X_HEADER] = current_request_id()

def ctx_celery_task_get_request_id():
    """
    Fetch the request id from the headers of the current celery task.
    """
    if current_task._get_current_object() is None:
        raise ExecutedOutsideContext()

    return current_task.request.get(_CELERY_X_HEADER, None)


# If you import this module then you are interested for this context
current_request_id.register_fetcher(ctx_celery_task_get_request_id)
