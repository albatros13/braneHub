import os
import json
import requests
import pytest
from src.OPAClient import OPAClient

OPA_URL = "http://localhost:8181"


def opa_running() -> bool:
    try:
        r = requests.get(f"{OPA_URL}/health", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="module")
def opa_client():
    if not opa_running():
        pytest.skip("OPA server is not running at http://localhost:8181; start OPA to run these tests.")
    return OPAClient(opa_url=OPA_URL)


def test_put_policy_and_query_onboarding(opa_client):
    # Load the simple onboarding acceptance policy from disk
    project_root = os.path.dirname(os.path.dirname(__file__))
    policy_path = os.path.join(project_root, "static", "data", "policies", "simple", "onboarding_acceptance.rego")
    with open(policy_path, "r", encoding="utf-8") as f:
        rego_text = f.read()

    # Use policy as-is (no unique package); upload under fixed policy id
    pid = "onboarding_acceptance"

    # Upload policy
    assert opa_client.put_policy(pid, rego_text) is True

    # Load input cases from JSON files
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(data_dir, "onboarding_acceptance_allow.json"), "r", encoding="utf-8") as f:
        allow_payload = json.load(f)
    with open(os.path.join(data_dir, "onboarding_acceptance_deny.json"), "r", encoding="utf-8") as f:
        deny_payload = json.load(f)

    # Query decision for the acceptable case
    allow_result = opa_client.query_data_path("simple/onboarding/decision", allow_payload.get("input", {}))
    assert isinstance(allow_result, dict), "OPA response should be an object"
    assert allow_result.get("allow") is True

    # Query decision for the unacceptable case
    deny_result = opa_client.query_data_path("simple/onboarding/decision", deny_payload.get("input", {}))
    assert isinstance(deny_result, dict), "OPA response should be an object"
    assert deny_result.get("allow") is False


