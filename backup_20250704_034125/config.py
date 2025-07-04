import os
from typing import Dict, Any

# API Keys - use environment variables in production
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_key_here")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your_anthropic_key_here")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "your_serpapi_key_here")

# LLM Configuration
LLM_CONFIG: Dict[str, Any] = {
    "openai": {
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "max_tokens": 2000,
    },
    "anthropic": {
        "model": "claude-3-5-sonnet-20241022",  # Claude-4-Sonnet equivalent
        "temperature": 0.1,
        "max_tokens": 2000,
    },
    "default_provider": "openai",
    "fallback_provider": "anthropic",
}

# Google Search Patching Configuration
GOOGLE_PATCH_ENABLED = os.getenv("GOOGLE_PATCH_ENABLED", "true").lower() == "true"

# Rate limiting
RATE_LIMIT = {
    "requests_per_minute": 30,
    "requests_per_hour": 500,
} 