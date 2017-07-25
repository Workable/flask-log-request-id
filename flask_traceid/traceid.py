import uuid
from flask import request, g
import logging as _logging

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


logger = _logging.getLogger(__name__)


class ContextualFilter(_logging.Filter):
    """
    Log filter to inject the trace id of the request
    """

    def filter(self, log_record):
        log_record.trace_id = current_trace_id()
        return log_record


def current_trace_id(raise_outside_context=False):
    """
    Get the current trace id for the served request
    :return: The trace id or None if it is executed out of context
    """
    top = stack.top
    if top is None:
        if raise_outside_context:
            raise RuntimeError("Requested current trace id outside context")
        return None  # Unknown trace id

    return g.get('_trace_id', None)


def get_amzn_elb_trace_id():
    """
    Get the amazon ELB trace id from request
    :param TraceID tracer: The trace id instance
    :return: The found Trace-ID or None if not found
    :rtype: str | None
    """
    amazon_request_id = request.headers.get('X-Amzn-Trace-Id', '')
    trace_id_params = dict(x.split('=') if '=' in x else (x, None) for x in amazon_request_id.split(';'))
    if 'Self' in trace_id_params:
        return trace_id_params['Self']
    if 'Root' in trace_id_params:
        return trace_id_params['Root']

    return None


class TraceID(object):

    def __init__(self, app=None, trace_id_extractor=None, trace_id_generator=None):
        """
        Initialize TraceID extension
        :param app: The flask application
        :param None | () -> str trace_id_extractor: The parser to extract traceid from request headers. Default is
         Amazon ELB parser.
        :param bool log_requests: A flag that if it is true it will add a log event at the end of request as werkzeug
        does but with the trace id included
        :param Callable trace_id_extractor: A callable to use in case of missing trace id.
        """
        self.app = app
        self._trace_id = None

        if trace_id_extractor is None:
            self._trace_id_extractor = get_amzn_elb_trace_id
        else:
            self._trace_id_extractor = trace_id_extractor

        if trace_id_generator is None:
            self._trace_id_generator = lambda: str(uuid.uuid4())
        else:
            self._trace_id_generator = trace_id_generator

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Register before request
        app.before_request(self._persist_trace_id)

        # Register after request
        if self.app.config.get('TRACEID_EMIT_REQUEST_LOG'):
            app.after_request(self._log_http_event)

    def _persist_trace_id(self):
        """
        It will extra and persist the TraceID from the HTTP request. If not
        found it will generate a new one.

        Intended usage is a handler of Flask.before_request event.
        :return:
        """
        g._trace_id = self._trace_id_extractor()
        if g._trace_id is None:
            g._trace_id = self._trace_id_generator()

    def _log_http_event(self, response):
        """
        It will create a log event as werkzeug but at the end of request holding the traceid

        Intended usage is a handler of Flask.after_request
        :return: The same response object
        """
        logger.info(
            '{ip} - - "{method} {path} {status_code}"'.format(
                ip=request.remote_addr,
                method=request.method,
                path=request.path,
                status_code=response.status_code)
        )
        return response
