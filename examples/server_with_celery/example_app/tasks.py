import logging
from .celery import celery


logger = logging.getLogger(__name__)


@celery.task()
def generic_add(a, b):
    print
    """Simple function to add two numbers"""
    logger.info('Called generic_add({}, {})'.format(a, b))
    return a + b
