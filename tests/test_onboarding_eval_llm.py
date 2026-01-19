import os
import json
import pytest
import re

from api.openai_client import llm_client as openai_client, OPENAI_MODEL
from api.anthropic_client import llm_client as anthropic_client, ANTHROPIC_MODEL

def get_llm_decision(client, model, input_data, provider="openai"):
    """
    Asks an LLM to decide whether to accept a participant.
    Logic: Accept if location is in acceptable_locations.
    Returns: {"allow": True/False}
    """
    prompt = f"""
    You are a policy evaluation engine.
    Decide whether to accept a participant based on the following input data:
    {json.dumps(input_data, indent=2)}

    Rule: Accept a participant (allow: true) if their location is within the acceptable_locations list. Otherwise, deny (allow: false).

    Return ONLY a JSON object in the following format:
    {{"allow": true}} or {{"allow": false}}
    """

    if provider == "openai":
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        result_text = response.choices[0].message.content
    elif provider == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result_text = response.content[0].text
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        # Fallback for LLMs that might include extra text
        match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

def load_test_data(filename):
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(project_root, "tests", "data", filename)
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- OpenAI Tests ---

@pytest.mark.openai
def test_openai_onboarding_allow():
    payload = load_test_data("onboarding_region_allow.json")
    result = get_llm_decision(openai_client, OPENAI_MODEL, payload.get("input", {}), provider="openai")
    assert isinstance(result, dict), "LLM response should be an object"
    assert result.get("allow") is True, f"OpenAI should have allowed. Input: {payload['input']}"

@pytest.mark.openai
def test_openai_onboarding_deny():
    payload = load_test_data("onboarding_region_deny.json")
    result = get_llm_decision(openai_client, OPENAI_MODEL, payload.get("input", {}), provider="openai")
    assert isinstance(result, dict), "LLM response should be an object"
    assert result.get("allow") is False, f"OpenAI should have denied. Input: {payload['input']}"

# --- Anthropic Tests ---

@pytest.mark.anthropic
def test_anthropic_onboarding_allow():
    payload = load_test_data("onboarding_region_allow.json")
    result = get_llm_decision(anthropic_client, ANTHROPIC_MODEL, payload.get("input", {}), provider="anthropic")
    assert isinstance(result, dict), "LLM response should be an object"
    assert result.get("allow") is True, f"Anthropic should have allowed. Input: {payload['input']}"

@pytest.mark.anthropic
def test_anthropic_onboarding_deny():
    payload = load_test_data("onboarding_region_deny.json")
    result = get_llm_decision(anthropic_client, ANTHROPIC_MODEL, payload.get("input", {}), provider="anthropic")
    assert isinstance(result, dict), "LLM response should be an object"
    assert result.get("allow") is False, f"Anthropic should have denied. Input: {payload['input']}"
