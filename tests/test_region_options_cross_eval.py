import os
import json
import pytest
import re
import requests
from src.OPAClient import OPAClient
from api.anthropic_client import llm_client as anthropic_client, ANTHROPIC_MODEL

OPA_URL = "http://localhost:8181"

def opa_running() -> bool:
    try:
        r = requests.get(f"{OPA_URL}/health", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

def get_llm_decision(client, model, location, acceptable_locations):
    """
    Asks Anthropic to decide whether to accept a participant.
    """
    input_data = {
        "location": location,
        "acceptable_locations": acceptable_locations
    }
    
    prompt = f"""
    You are a policy evaluation engine.
    Decide whether to accept a participant based on the following input data:
    {json.dumps(input_data, indent=2)}

    Rule: Accept a participant (allow: true) if their location is a valid representation or sub-region of one of the acceptable_locations. 
    Be flexible with synonyms and well-known regions (e.g., "NL" for "Netherlands", "London" for "United Kingdom").
    Otherwise, deny (allow: false).

    Return ONLY a JSON object in the following format:
    {{"allow": true}} or {{"allow": false}}
    """

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result_text = response.content[0].text
        
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
    except Exception as e:
        print(f"Error calling Anthropic: {e}")
        return {"allow": False, "error": str(e)}

@pytest.mark.skipif(not opa_running(), reason="OPA server not running")
def test_cross_evaluation_region_options():
    # 1. Setup OPA
    opa_client = OPAClient(opa_url=OPA_URL)
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    # Simple Policy
    policy_path = os.path.join(project_root, "static", "data", "policies", "simple", "onboarding_region.rego")
    with open(policy_path, "r", encoding="utf-8") as f:
        rego_text = f.read()
    pid_simple = "onboarding_simple"
    assert opa_client.put_policy(pid_simple, rego_text) is True

    # Extended Policy (Plus)
    policy_plus_path = os.path.join(project_root, "static", "data", "policies", "simple", "onboarding_region_plus.rego")
    with open(policy_plus_path, "r", encoding="utf-8") as f:
        rego_plus_text = f.read()
    pid_plus = "onboarding_plus"
    assert opa_client.put_policy(pid_plus, rego_plus_text) is True

    # 2. Load Region Options
    options_path = os.path.join(project_root, "tests", "data", "region_options.json")
    with open(options_path, "r", encoding="utf-8") as f:
        region_options = json.load(f)

    results = {}

    # 3. Iterate and Evaluate
    for expected_region, options in region_options.items():
        results[expected_region] = {
            "total": len(options),
            "rego_simple_accepted": 0,
            "rego_plus_accepted": 0,
            "llm_accepted": 0,
            "details": []
        }
        
        acceptable_locations = [expected_region]
        
        for option in options:
            # Rego Simple Evaluation
            rego_simple_res = opa_client.query_data_path("simple/onboarding/decision", {
                "location": option,
                "acceptable_locations": acceptable_locations
            })
            rego_simple_allow = rego_simple_res.get("allow", False) if isinstance(rego_simple_res, dict) else False
            if rego_simple_allow:
                results[expected_region]["rego_simple_accepted"] += 1
            
            # Rego Plus Evaluation
            rego_plus_res = opa_client.query_data_path("simple/onboarding_plus/decision", {
                "location": option,
                "acceptable_locations": acceptable_locations
            })
            rego_plus_allow = rego_plus_res.get("allow", False) if isinstance(rego_plus_res, dict) else False
            if rego_plus_allow:
                results[expected_region]["rego_plus_accepted"] += 1
                
            # LLM Evaluation
            llm_res = get_llm_decision(anthropic_client, ANTHROPIC_MODEL, option, acceptable_locations)
            llm_allow = llm_res.get("allow", False)
            if llm_allow:
                results[expected_region]["llm_accepted"] += 1
            
            results[expected_region]["details"].append({
                "option": option,
                "rego_simple": rego_simple_allow,
                "rego_plus": rego_plus_allow,
                "llm": llm_allow
            })

    # 4. Report
    print("\nCross-Evaluation Summary (Rego Simple vs Rego Plus vs Anthropic):")
    print(f"{'Region':<20} | {'Total':<5} | {'Simple':<8} | {'Plus':<8} | {'LLM Acc':<8}")
    print("-" * 75)
    for region, stat in results.items():
        print(f"{region:<20} | {stat['total']:<5} | {stat['rego_simple_accepted']:<8} | {stat['rego_plus_accepted']:<8} | {stat['llm_accepted']:<8}")

    # Optionally, you can add assertions or save the results to a file
    # For now, we'll just print them as requested.
