import unittest
from orchestrator import Orchestrator
from micro.scrape import ScrapeMicroFunction
from micro.enrich import EnrichMicroFunction
from micro.draft import DraftMicroFunction
from micro.critique import CritiqueMicroFunction
from micro.render import RenderMicroFunction
from micro.qa import QAMicroFunction

class TestOrchestrator(unittest.TestCase):
    def test_pipeline(self):
        steps = [
            ScrapeMicroFunction(),
            EnrichMicroFunction(),
            DraftMicroFunction(),
            QAMicroFunction(),
            CritiqueMicroFunction(),
            RenderMicroFunction(),
        ]
        orchestrator = Orchestrator(steps)
        result = orchestrator.run({"input": "Test job posting"})
        self.assertIn("scraped_text", result)
        self.assertIn("enriched", result)
        self.assertIn("draft", result)
        self.assertIn("qa_result", result)
        self.assertIn("critique", result)
        self.assertIn("rendered_markdown", result)

if __name__ == "__main__":
    unittest.main() 