package federated.audit

import future.keywords.if

# Log all decisions
log_decision[decision] {
    decision := {
        "timestamp": time.now_ns(),
        "policy": "enrollment",
        "client_id": input.client.id,
        "decision": data.federated.enrollment.allow,
        "reasons": data.federated.enrollment.reasons
    }
}