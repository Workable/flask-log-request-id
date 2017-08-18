from celery import Task, current_task

from ..request_id import current_request_id
from ..ctx_fetcher import ExecutedOutsideContext

_CELERY_X_HEADER = 'x_request_id'


class RequestIDAwareTask(Task):
    """
    Task base class that injects request id to task request object with key 'x_request_id'.
    """
    abstract = True

    def apply_async(self, *args, **kwargs):
        # Override to inject trace id
        kwargs.setdefault('headers', {})
        kwargs['headers'][_CELERY_X_HEADER] = current_request_id()
        return super(RequestIDAwareTask, self).apply_async(*args, **kwargs)


def ctx_celery_task_get_request_id():
    """
    Fetch the request id from the headers of the current celery task.
    """
    if current_task._get_current_object() is None:
        raise ExecutedOutsideContext()

    return current_task.request.get(_CELERY_X_HEADER, None)


def configure_celery(celery_app):
    """
    Configure celery application to forward current request id to delegated tasks
    :param celery.App celery_app: The application instance to configure
    """
    # Configure celery app
    celery_app.Task = RequestIDAwareTask

    # Register context fetcher
    current_request_id.register_fetcher(ctx_celery_task_get_request_id)
