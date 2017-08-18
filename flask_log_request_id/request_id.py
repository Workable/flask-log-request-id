import uuid
import logging as _logging

from flask import request, g, current_app
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
    Log filter to inject the current request id of the request under `log_record.request_id`

    """

    def filter(self, log_record):
        log_record.request_id = current_request_id()
        return log_record


def current_request_id(raise_outside_context=False):
    """
    Get the current request id for the served request
    :return: The request id or None if it is executed out of context
    """
    top = stack.top
    if top is None:
        if raise_outside_context:
            raise RuntimeError("Requested current request id outside context")
        return None  # Unknown request id
    g_object_attr = current_app.config['LOG_REQUEST_ID_G_OBJECT_ATTRIBUTE']

    return g.get(g_object_attr, None)


class RequestID(object):
    """
    Flask extension to parse or generate the id of each request
    """

    def __init__(self, app=None, request_id_parser=None, request_id_generator=None):
        """
        Initialize extension
        :param flask.Application | None app: The flask application or None if you want to initialize later
        :param None | () -> str request_id_parser: The parser to extract request-id from request headers. If None
        the default auto_parser() will be used that will try all known parsers.
        :param ()->str request_id_generator: A callable to use in case of missing request-id.
        """
        self.app = app
        self._request_id = None

        self._request_id_parser = request_id_parser
        if self._request_id_parser is None:
            self._request_id_parser = auto_parser

        self._request_id_generator = request_id_generator
        if self._request_id_generator is None:
            self._request_id_generator = lambda: str(uuid.uuid4())

        self._generate_id_if_not_found = True

        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        # Default configuration
        app.config.setdefault('LOG_REQUEST_ID_GENERATE_IF_NOT_FOUND', True)
        app.config.setdefault('LOG_REQUEST_ID_LOG_ALL_REQUESTS', False)
        app.config.setdefault('LOG_REQUEST_ID_G_OBJECT_ATTRIBUTE', 'log_request_id')

        # Register before request callback
        @app.before_request
        def _persist_request_id():
            """
            It will parse and persist the RequestID from the HTTP request. If not
            found it will generate a new one if requestsed.

            To be used as a consumer of Flask.before_request event.
            """
            g_object_attr = current_app.config['LOG_REQUEST_ID_G_OBJECT_ATTRIBUTE']

            setattr(g, g_object_attr, self._request_id_parser())
            if g.get(g_object_attr) is None:
                if app.config['LOG_REQUEST_ID_GENERATE_IF_NOT_FOUND']:
                    setattr(g, g_object_attr, self._request_id_generator())

        # Register after request
        if self.app.config['LOG_REQUEST_ID_LOG_ALL_REQUESTS']:
            app.after_request(self._log_http_event)

    @staticmethod
    def _log_http_event(response):
        """
        It will create a log event as werkzeug but at the end of request holding the request-id

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
