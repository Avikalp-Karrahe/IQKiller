import unittest
from metrics import log_metric
import io
import sys

class TestMetrics(unittest.TestCase):
    def test_log_metric(self):
        captured = io.StringIO()
        sys.stdout = captured
        log_metric("test_event", {"foo": "bar"})
        sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn('"event": "test_event"', output)
        self.assertIn('"foo": "bar"', output)

if __name__ == "__main__":
    unittest.main() 