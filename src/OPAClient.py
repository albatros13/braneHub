import requests
import json


class OPAClient:
    def __init__(self, opa_url="http://localhost:8181"):
        self.opa_url = opa_url

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