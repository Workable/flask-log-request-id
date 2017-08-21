import logging
from random import randint
from flask import Flask
from flask_log_request_id import RequestID, RequestIDLogFilter

from .celery import celery
from . import tasks

logger = logging.getLogger(__name__)


def initialize_logging():
    # Setup logging
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - level=%(levelname)s - request_id=%(request_id)s - %(message)s"))
    handler.addFilter(RequestIDLogFilter())  # << Add request id contextual filter
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)


app = Flask(__name__)
app.config['LOG_REQUEST_ID_LOG_ALL_REQUESTS'] = True
RequestID(app)
initialize_logging()


@ app.route('/')
def index():
    a, b = randint(1, 15), randint(1, 15)
    logger.info('Adding two random numbers {} {}'.format(a, b))
    task = tasks.generic_add.delay(a, b)

    return "Task {!s} started".format(task)
