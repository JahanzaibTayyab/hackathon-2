"""Custom model provider for OpenAI."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from agents import ModelProvider, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_NAME = "gpt-4o-mini"  # Using GPT-4o-mini for cost efficiency

# Validate API key
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please set it in your .env file. "
        "Get your API key from https://platform.openai.com/api-keys"
    )

# Create AsyncOpenAI client
openai_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
)


class OpenAIModelProvider(ModelProvider):
    """Model provider for OpenAI."""

    def get_model(self, model_name: str | None) -> OpenAIChatCompletionsModel:
        """
        Get model instance configured for OpenAI.

        Args:
            model_name: Optional model name override

        Returns:
            OpenAIChatCompletionsModel configured for OpenAI
        """
        return OpenAIChatCompletionsModel(
            model=model_name or OPENAI_MODEL_NAME,
            openai_client=openai_client,
        )


# Global instance to use in runners
openai_provider = OpenAIModelProvider()
