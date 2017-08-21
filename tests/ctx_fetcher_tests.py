import unittest
import mock
from flask_log_request_id.ctx_fetcher import MultiContextRequestIdFetcher, ExecutedOutsideContext


class CtxFetcherTestCase(unittest.TestCase):

    def test_empty_multictx_fetcher(self):
        fetcher = MultiContextRequestIdFetcher()

        self.assertIsNone(fetcher())

    def test_register_ctx_fetcher(self):
        fetcher = MultiContextRequestIdFetcher()

        ctx_fetcher = mock.Mock()

        # One fetcher in context
        ctx_fetcher.return_value = 'response'
        fetcher.register_fetcher(ctx_fetcher)
        self.assertEqual(fetcher(), 'response')

        # One fetcher outside context
        ctx_fetcher.side_effect = ExecutedOutsideContext
        self.assertIsNone(fetcher())

    def test_register_multiple_fetcher(self):
        multi_fetcher = MultiContextRequestIdFetcher()

        ctx_fetchers = [
            mock.Mock(),
            mock.Mock()]
        for index, f in enumerate(ctx_fetchers):
            multi_fetcher.register_fetcher(f)
            f.return_value = "fetcher:{}".format(index)

        # Second is in context
        ctx_fetchers[0].side_effect = ExecutedOutsideContext
        self.assertEqual(multi_fetcher(), 'fetcher:1')

        # None is in context
        ctx_fetchers[1].side_effect = ExecutedOutsideContext
        self.assertIsNone(multi_fetcher())

        # Both in context
        ctx_fetchers[0].side_effect = None
        ctx_fetchers[1].side_effect = None
        self.assertEqual(multi_fetcher(), 'fetcher:0')

    def test_register_same_fetcher(self):
        multi_fetcher = MultiContextRequestIdFetcher()

        fetcher1 = mock.Mock()
        multi_fetcher.register_fetcher(fetcher1)
        self.assertEqual(
            multi_fetcher.ctx_fetchers,
            [fetcher1]
        )

        # Re-register
        multi_fetcher.register_fetcher(fetcher1)
        self.assertEqual(
            multi_fetcher.ctx_fetchers,
            [fetcher1]
        )



if __name__ == '__main__':
    unittest.main()
