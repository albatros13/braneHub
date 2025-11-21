import os
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("❌ Configuration error: OPENAI_API_KEY not found in environment or .env file.")
    raise RuntimeError(
        "Configuration error: OPENAI_API_KEY not found. "
        "Please set it as an environment variable or in your .env file."
    )

llm_client = OpenAI(api_key=OPENAI_API_KEY)


