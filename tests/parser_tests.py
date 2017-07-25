import unittest

from flask import Flask

from flask_traceid.parser import amazon_elb_trace_id, x_correlation_id, x_request_id, auto_parser


class AmazonELBTraceIdTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)

    def test_with_header_only_root(self):
        with self.app.test_request_context(headers={'X-Amzn-Trace-Id': 'Root=1-67891233-abc'}):
            self.assertEqual('1-67891233-abc', amazon_elb_trace_id())

    def test_with_header_root_and_self(self):
        with self.app.test_request_context(headers={'X-Amzn-Trace-Id': 'Self=1-67891234-def;Root=1-67891233-abc'}):
            self.assertEqual('1-67891234-def', amazon_elb_trace_id())

    def test_with_header_root_self_and_custom_params(self):
        with self.app.test_request_context(headers={'X-Amzn-Trace-Id': 'Self=1-def;Root=1-abc;CalledFrom=app'}):
            self.assertEqual('1-def', amazon_elb_trace_id())

    def test_without_header(self):
        with self.app.test_request_context():
            self.assertIsNone(amazon_elb_trace_id())

    def test_with_invalid_header(self):
        with self.app.test_request_context(headers={'X-Amzn-Trace-Id': 'ohmythisisnotvalid'}):
            self.assertIsNone(amazon_elb_trace_id())


class RequestIDIdTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)

    def test_x_request_id_empty_header(self):

        with self.app.test_request_context():
            # No header should return empty
            self.assertIsNone(x_request_id())

    def test_x_request_id_invalid_header(self):
        with self.app.test_request_context(headers={'X-Request-ID': ''}):
            # Wrong header
            self.assertIsNone(x_request_id())

    def test_x_request_id_valid_header(self):
        with self.app.test_request_context(headers={'X-Request-ID': '1-67891233-root'}):
            # Simple request id
            self.assertEqual('1-67891233-root', x_request_id())

    def test_x_request_id_wrong_sensitivity(self):
        with self.app.test_request_context(headers={'x-request-id': '1-67891233-root'}):
            # Simple request with case insensitivity
            self.assertEqual('1-67891233-root', x_request_id())


class CorrelationIDIdTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)

    def test_x_correlation_id_empty_header(self):

        with self.app.test_request_context():
            # No header should return empty
            self.assertIsNone(x_correlation_id())

    def test_x_correlation_id_invalid_header(self):
        with self.app.test_request_context(headers={'X-Correlation-ID': ''}):
            # Wrong header
            self.assertIsNone(x_correlation_id())

    def test_x_correlation_id_valid_header(self):
        with self.app.test_request_context(headers={'X-Correlation-ID': '1-67891233-root'}):
            # Simple request id
            self.assertEqual('1-67891233-root', x_correlation_id())

    def test_x_correlation_id_wrong_sensitivity(self):
        with self.app.test_request_context(headers={'x-correlation-id': '1-67891233-root'}):
            # Simple request with case insensitivity
            self.assertEqual('1-67891233-root', x_correlation_id())


class AutoParserTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)

    def test_auto_parser_empty_header(self):

        with self.app.test_request_context():
            # No header should return empty
            self.assertIsNone(auto_parser())

    def test_auto_parser_invalid_header(self):
        with self.app.test_request_context(headers={
            'X-Amzn-Trace-Id': '',
            'X-Correlation-ID': '',
            'X-Request-ID': ''
        }):
            # Wrong headers
            self.assertIsNone(auto_parser())

    def test_auto_parser_precedence_1(self):
        with self.app.test_request_context(headers={
            'X-Amzn-Trace-Id': 'Root=1-67891233-root',
            'X-Correlation-ID': '1-67891233-correlation',
            'X-Request-ID': '1-67891233-request-id'
        }):
            # Precedence scenario 1
            self.assertEqual('1-67891233-request-id', auto_parser())

    def test_auto_parser_precedence_2(self):
        with self.app.test_request_context(headers={
            'X-Amzn-Trace-Id': 'Root=1-67891233-root',
            'X-Correlation-ID': '1-67891233-correlation',
        }):
            # Precedence scenario 1
            self.assertEqual('1-67891233-correlation', auto_parser())


if __name__ == '__main__':
    unittest.main()
