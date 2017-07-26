import uuid
import logging as _logging

from flask import request, g
from .parser import auto_parser


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


class TraceID(object):

    def __init__(self, app=None, trace_id_parser=None, trace_id_generator=None):
        """
        Initialize TraceID extension
        :param app: The flask application
        :param None | () -> str trace_id_parser: The parser to extract traceid from request headers. Default is
         Amazon ELB parser.
        :param ()->str trace_id_extractor: A callable to use in case of missing trace id.
        """
        self.app = app
        self._trace_id = None

        self._trace_id_parser = trace_id_parser
        if self._trace_id_parser is None:
            self._trace_id_parser = auto_parser

        self._trace_id_generator = trace_id_generator
        if self._trace_id_generator is None:
            self._trace_id_generator = lambda: str(uuid.uuid4())

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
        g._trace_id = self._trace_id_parser()
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
