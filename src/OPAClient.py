import requests
import json


class OPAClient:
    def __init__(self, opa_url="http://localhost:8181"):
        self.opa_url = opa_url

    def put_policy(self, policy_id: str, rego_text: str):
        """Upload or replace a policy in OPA.
        Args:
            policy_id: identifier for the policy in OPA (e.g., 'data_format_acceptance')
            rego_text: the policy content in Rego language
        Returns True on success, raises on HTTP error.
        """
        url = f"{self.opa_url}/v1/policies/{policy_id}"
        resp = requests.put(url, data=rego_text.encode('utf-8'), headers={"Content-Type": "text/plain"})
        resp.raise_for_status()
        return True

    def query_data_path(self, data_path: str, input_obj: dict):
        """Query a data path decision endpoint (REST) with given input.
        data_path: e.g., 'data/format/decision' or 'data/data/format/decision' depending on package
        Returns the 'result' field from OPA response.
        """
        # Ensure the path starts without leading slash
        path = data_path.lstrip('/')
        url = f"{self.opa_url}/v1/data/{path}"
        payload = {"input": input_obj}
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        body = resp.json()
        return body.get("result")

    def evaluate_data_format(self, rego_text: str, input_obj: dict, policy_id: str = "data_format_acceptance"):
        """Convenience method to evaluate our data.format.decision policy.
        - Uploads the policy to OPA with the given policy_id
        - Queries the decision at package data.format rule decision (REST path /v1/data/data/format/decision)
        Returns the result object (with allow, deny_reasons, requirements, notes) or None if not found.
        """
        # Upload policy
        self.put_policy(policy_id, rego_text)
        # Query decision (package is 'data.format' -> REST path 'data/format/decision' prefixed by implicit root 'data')
        # In REST, full path includes implicit root 'data', so becomes 'data/format/decision' under /v1/data/, i.e., /v1/data/data/format/decision
        return self.query_data_path("data/format/decision", input_obj)

    def check_enrollment(self, client_info):
        """Check if client can enroll"""
        policy_path = "v1/data/federated/enrollment/allow"

        payload = {
            "input": {
                "client": client_info
            }
        }

        response = requests.post(
            f"{self.opa_url}/{policy_path}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        result = response.json()
        return result.get("result", False)

    def validate_model_update(self, client_id, model_data, round_number):
        """Validate model update from client"""
        policy_path = "v1/data/federated/model_validation/allow"

        payload = {
            "input": {
                "client": {"id": client_id},
                "model": model_data,
                "round_number": round_number
            }
        }

        response = requests.post(
            f"{self.opa_url}/{policy_path}",
            json=payload
        )

        result = response.json()
        return result.get("result", False)

    def check_aggregation(self, participants, round_info):
        """Check if aggregation can proceed"""
        policy_path = "v1/data/federated/aggregation/allow_aggregation"

        payload = {
            "input": {
                "participants": participants,
                "round": round_info
            }
        }

        response = requests.post(
            f"{self.opa_url}/{policy_path}",
            json=payload
        )

        result = response.json()
        return result.get("result", False)


# Usage in FL Server
class FederatedServer:
    def __init__(self):
        self.opa = OPAClient()
        self.enrolled_clients = []

    def enroll_client(self, client_info):
        """Enroll a new client"""
        # Check with OPA
        if not self.opa.check_enrollment(client_info):
            return {"status": "denied", "reason": "Policy violation"}

        # Proceed with enrollment
        self.enrolled_clients.append(client_info)
        return {"status": "accepted", "client_id": client_info["id"]}

    def receive_model_update(self, client_id, model_data, round_number):
        """Receive and validate model update"""
        # Validate with OPA
        if not self.opa.validate_model_update(client_id, model_data, round_number):
            return {"status": "rejected", "reason": "Invalid model update"}

        # Process the model update
        self.process_update(client_id, model_data)
        return {"status": "accepted"}

    def aggregate_models(self, round_number):
        """Aggregate models from participants"""
        participants = self.get_round_participants(round_number)
        round_info = {"number": round_number, "epsilon_cost": 0.5}

        # Check aggregation policy
        if not self.opa.check_aggregation(participants, round_info):
            return {"status": "failed", "reason": "Aggregation policy not satisfied"}

        # Perform aggregation
        aggregated_model = self.perform_aggregation(participants)
        return {"status": "success", "model": aggregated_model}