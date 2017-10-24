import mock
import unittest

from celery import Celery
from flask_log_request_id.extras.celery import (ExecutedOutsideContext,
                                                RequestIDAwareTask,
                                                add_request_id_header,
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
    def test_mixin_injection(self, mocked_current_request_id):

        patcher = mock.patch.object(RequestIDAwareTask, '__bases__', (MockedTask,))

        with patcher:
            patcher.is_local = True

            mocked_current_request_id.return_value = 15
            task = RequestIDAwareTask()
            task.apply_async('test', foo='bar')
            self.assertEqual(
                task.apply_async_called['args'],
                ('test', ))

            self.assertDictEqual(
                task.apply_async_called['kwargs'], {
                    'headers': {'x_request_id': 15},
                    'foo': 'bar'
            })

    @mock.patch('flask_log_request_id.extras.celery.current_request_id')
    def test_issue21_called_with_headers_None(self, mocked_current_request_id):

        patcher = mock.patch.object(RequestIDAwareTask, '__bases__', (MockedTask,))

        with patcher:
            patcher.is_local = True

            mocked_current_request_id.return_value = 15
            task = RequestIDAwareTask()
            task.apply_async('test', foo='bar', headers=None)
            self.assertEqual(
                task.apply_async_called['args'],
                ('test', ))

            self.assertDictEqual(
                task.apply_async_called['kwargs'], {
                    'headers': {'x_request_id': 15},
                    'foo': 'bar'
            })

    @mock.patch('flask_log_request_id.extras.celery.current_request_id')
    def test_before_task_publish_hooks_adds_header(self, mocked_current_request_id):
        mocked_current_request_id.return_value = 15

        headers = {}
        add_request_id_header(headers={})
        print(headers)
        self.assertDictEqual(headers, {
            'x_request_id': 15
        })

    @mock.patch('flask_log_request_id.extras.celery.current_task')
    def test_ctx_fetcher_outside_context(self, mocked_current_task):

        mocked_current_task._get_current_object.return_value = None
        with self.assertRaises(ExecutedOutsideContext):
            ctx_celery_task_get_request_id()

    @mock.patch('flask_log_request_id.extras.celery.current_task')
    def test_ctx_fetcher_inside_context(self, mocked_current_task):
        mocked_current_task._get_current_object.return_value = True
        mocked_current_task.request.get.side_effect = lambda a, default: {'x_request_id': 15, 'other':'bar'}[a]

        self.assertEqual(ctx_celery_task_get_request_id(), 15)


if __name__ == '__main__':
    unittest.main()
