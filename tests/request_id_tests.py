import flask
import unittest

from flask_log_request_id.request_id import RequestID, current_request_id
from mock import patch


class RequestIDTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)

        self.app.route('/')(lambda: 'hello world')
        self.app.testing = True

    def test_default_request_id_parser_with_amazon(self):
        RequestID(self.app)
        with self.app.test_request_context(headers={'X-Amzn-Trace-Id': 'Self=1-67891234-def;Root=1-67891233-abc'}):
            self.app.preprocess_request()
            self.assertEqual('1-67891234-def', current_request_id())

    def test_default_request_id_parser_with_request_id(self):
        RequestID(self.app)
        with self.app.test_request_context(headers={'X-Request-Id': '1-67891234-def'}):
            self.app.preprocess_request()
            self.assertEqual('1-67891234-def', current_request_id())

    def test_custom_request_id_parser(self):
        RequestID(self.app, request_id_parser=lambda: 'fixedid')
        with self.app.test_request_context():
            self.app.preprocess_request()
            self.assertEqual('fixedid', current_request_id(None))

    @patch('flask_log_request_id.request_id.uuid.uuid4')
    def test_default_generator(self, mock_uuid4):
        mock_uuid4.return_value = 'abc-123'
        RequestID(self.app)
        with self.app.test_request_context():
            self.app.preprocess_request()
            self.assertEqual('abc-123', current_request_id(None))

    def test_custom_generator(self):
        RequestID(self.app, request_id_generator=lambda: 'def-456')
        with self.app.test_request_context():
            self.app.preprocess_request()
            self.assertEqual('def-456', current_request_id(None))

    @patch('flask_log_request_id.request_id.logger')
    def test_log_request_when_enabled(self, mock_logger):
        self.app.config.update({
            'REQUESTID_EMIT_REQUEST_LOG': True
        })
        RequestID(self.app)

        client = self.app.test_client()
        rv = client.get('/')
        self.assertTrue(b'hello world' in rv.data)

        mock_logger.info.assert_called_once_with('127.0.0.1 - - "GET / 200"')

    @patch('flask_log_request_id.request_id.logger')
    def test_log_request_disabled(self, mock_logger):
        RequestID(self.app)
        with self.app.test_request_context('/test'):
            pass

        mock_logger.info.assert_not_called()
