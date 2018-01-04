import mock
import unittest

from celery import Celery
from flask_log_request_id.extras.celery import (ExecutedOutsideContext,
                                                on_before_publish_insert_request_id_header,
                                                ctx_celery_task_get_request_id)


class MockedTask(object):

    def __init__(self):
        self.apply_async_called = None

    def apply_async(self, *args, **kwargs):
        self.apply_async_called = {
            'args': args,
            'kwargs': kwargs
        }


class CeleryIntegrationTestCase(unittest.TestCase):

    @mock.patch('flask_log_request_id.extras.celery.current_request_id')
    def test_enable_request_id_propagation(self, mocked_current_request_id):
        mocked_current_request_id.return_value = 15

        headers = {}
        on_before_publish_insert_request_id_header(headers=headers)
        self.assertDictEqual(
            {
                'x_request_id': 15
            },
            headers)

    @mock.patch('flask_log_request_id.extras.celery.current_task')
    def test_ctx_fetcher_outside_context(self, mocked_current_task):
        mocked_current_task._get_current_object.return_value = None
        with self.assertRaises(ExecutedOutsideContext):
            ctx_celery_task_get_request_id()

    @mock.patch('flask_log_request_id.extras.celery.current_task')
    def test_ctx_fetcher_inside_context(self, mocked_current_task):
        mocked_current_task._get_current_object.return_value = True
        mocked_current_task.request.get.side_effect = lambda a, default: {'x_request_id': 15, 'other': 'bar'}[a]

        self.assertEqual(ctx_celery_task_get_request_id(), 15)


if __name__ == '__main__':
    unittest.main()
