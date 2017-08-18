import logging
from random import randint
from flask import Flask
from flask_log_request_id import RequestID, ContextualFilter

logger = logging.getLogger(__name__)


def generic_add(a, b):
    """Simple function to add two numbers"""
    logger.debug('Called generic_add({}, {})'.format(a, b))
    return a + b

app = Flask(__name__)
app.config['REQUESTID_EMIT_REQUEST_LOG'] = True
RequestID(app)

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - level=%(levelname)s - request_id=%(request_id)s - %(message)s"))
handler.addFilter(ContextualFilter())  # << Add request id contextual filter
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)


@ app.route('/')
def index():
    a, b = randint(1, 15), randint(1, 15)
    logger.info('Adding two random numbers {} {}'.format(a, b))
    return str(generic_add(a, b))


if __name__ == '__main__':
    app.run(debug=True)