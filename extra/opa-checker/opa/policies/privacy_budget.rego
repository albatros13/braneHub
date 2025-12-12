package federated.privacy

import future.keywords.if

default allow := false

# Allow operation if privacy budget permits
allow if {
    within_epsilon_budget
    within_delta_budget
    client_contribution_limit_ok
}

within_epsilon_budget if {
    current := data.privacy_state.epsilon_spent
    requested := input.operation.epsilon_cost
    total := current + requested
    total <= data.privacy_config.total_epsilon_budget
}

within_delta_budget if {
    current := data.privacy_state.delta_spent
    requested := input.operation.delta_cost
    total := current + requested
    total <= data.privacy_config.total_delta_budget
}

# Limit how much one client can contribute (防止单点隐私泄露)
client_contribution_limit_ok if {
    client_id := input.client.id
    client_contributions := [c | c := data.privacy_state.contributions[_]; c.client_id == client_id]
    count(client_contributions) < data.privacy_config.max_contributions_per_client
}

# Calculate remaining budget
remaining_budget := {
    "epsilon": data.privacy_config.total_epsilon_budget - data.privacy_state.epsilon_spent,
    "delta": data.privacy_config.total_delta_budget - data.privacy_state.delta_spent,
    "client_contributions_left": data.privacy_config.max_contributions_per_client - count([c | c := data.privacy_state.contributions[_]; c.client_id == input.client.id])
}