package federated.model_validation

import future.keywords.if
import future.keywords.in

default allow := false

# Allow model update if valid
allow if {
    valid_model_size
    valid_parameter_count
    valid_gradient_norm
    no_suspicious_patterns
    client_authorized
}

# Check model size is within bounds
valid_model_size if {
    input.model.size_bytes <= data.limits.max_model_size_mb * 1048576
    input.model.size_bytes >= data.limits.min_model_size_mb * 1048576
}

# Check parameter count matches expected
valid_parameter_count if {
    input.model.parameter_count == data.model_config.expected_parameters
}

# Check gradient norm (防止梯度爆炸攻击)
valid_gradient_norm if {
    input.model.gradient_norm <= data.security.max_gradient_norm
}

# Detect suspicious patterns
no_suspicious_patterns if {
    not has_nan_values
    not has_extreme_outliers
}

has_nan_values if {
    input.model.contains_nan == true
}

has_extreme_outliers if {
    input.model.max_parameter_value > data.security.parameter_threshold
}

# Check client is authorized for this round
client_authorized if {
    input.client.id in data.current_round.selected_clients
}

# Validation report
validation_report := {
    "valid": allow,
    "client_id": input.client.id,
    "round": input.round_number,
    "checks": {
        "size": valid_model_size,
        "parameters": valid_parameter_count,
        "gradient_norm": valid_gradient_norm,
        "no_suspicious": no_suspicious_patterns,
        "authorized": client_authorized
    }
}