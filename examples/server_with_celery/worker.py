import logging.config
from example_app import tasks, celery
from flask_log_request_id import RequestIDLogFilter


def initialize_celery_logging():
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'request_id_filter': {
                '()': RequestIDLogFilter
            },
        },
        'formatters': {
            'simple_request_id': {
                'format': "{asctime} - {name} - level={levelname} - request_id={request_id} - {message}",
                'style': '{'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple_request_id',
                'filters': ['request_id_filter']
            }
        },
        'loggers': {
            'example_app': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': 'no',
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
    logging.config.dictConfig(LOGGING)

initialize_celery_logging()


