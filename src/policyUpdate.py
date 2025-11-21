import requests

def update_opa_policy(policy_name, policy_content):
    """Update OPA policy dynamically"""
    url = f"http://localhost:8181/v1/policies/{policy_name}"
    response = requests.put(
        url,
        data=policy_content,
        headers={"Content-Type": "text/plain"}
    )
    return response.status_code == 200

def update_opa_data(path, data):
    """Update OPA data dynamically"""
    url = f"http://localhost:8181/v1/data/{path}"
    response = requests.put(
        url,
        json=data
    )
    return response.status_code == 204