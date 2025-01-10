import asyncio
import unittest

from lib.v1.dummy_game import async_simple_game_function


class TestDummyGame(unittest.TestCase):
    def test_async_simple_game_function(self):
        """
        Check that SystemExit is raised at end of function, not any
        other exception such as file not found or somthing else.
        """
        test_frame_limit = 20
        raised_exception = None

        try:
            asyncio.run(async_simple_game_function(frame_limit=test_frame_limit))
        except SystemExit as e:
            # SystemExit doesn't inherit from BaseException, so
            # explicitly catch it
            raised_exception = e
        except Exception as e:
            # Also catch any other exceptions that could occur
            raised_exception = e

        self.assertIsInstance(raised_exception, SystemExit)


if __name__ == "__main__":
    unittest.main()
