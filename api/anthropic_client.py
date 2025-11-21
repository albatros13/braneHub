import base64
import os
from anthropic import Anthropic, APIError
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    logger.error("❌ Configuration error: ANTHROPIC_API_KEY not found in environment or .env file.")
    raise RuntimeError(
        "Configuration error: ANTHROPIC_API_KEY not found. "
        "Please set it as an environment variable or in your .env file."
    )

# Initialize Claude client
llm_client = Anthropic(api_key=ANTHROPIC_API_KEY)



