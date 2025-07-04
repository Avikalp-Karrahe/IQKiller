import unittest
import yaml

class TestPrompts(unittest.TestCase):
    def test_load_prompts(self):
        with open("prompts/v1.yaml") as f:
            prompts = yaml.safe_load(f)
        for key in ["scrape_prompt", "enrich_prompt", "draft_prompt", "critique_prompt", "qa_prompt"]:
            self.assertIn(key, prompts)

if __name__ == "__main__":
    unittest.main() 