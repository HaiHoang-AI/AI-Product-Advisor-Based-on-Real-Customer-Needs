"""LLM client wrapper — abstracts Gemini API calls."""
from __future__ import annotations

import json
import logging
from typing import Any

from google import genai
from google.genai import types

from backend.config import settings

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def get_client() -> genai.Client:
    """Get or create the Gemini client singleton."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


async def llm_generate(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.3,
    response_mime_type: str | None = None,
    response_schema: Any = None,
) -> str:
    """Generate text using Gemini."""
    client = get_client()

    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=4096,
    )
    if system_instruction:
        config.system_instruction = system_instruction
    if response_mime_type:
        config.response_mime_type = response_mime_type
    if response_schema:
        config.response_schema = response_schema

    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt,
        config=config,
    )
    return response.text or ""


async def llm_generate_json(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.2,
) -> dict | list:
    """Generate structured JSON output from Gemini."""
    result = await llm_generate(
        prompt=prompt,
        system_instruction=system_instruction,
        temperature=temperature,
        response_mime_type="application/json",
    )
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON from LLM: {result[:200]}")
        # Try to extract JSON from markdown code block
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        if "```" in result:
            json_str = result.split("```")[1].split("```")[0].strip()
            return json.loads(json_str)
        raise
