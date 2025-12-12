package federated.enrollment

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false

# Allow enrollment if all conditions are met
allow if {
    client_authenticated
    client_meets_requirements
    not client_blacklisted
    enrollment_window_open
}

# Check if client is authenticated
client_authenticated if {
    input.client.certificate_valid
    input.client.identity != ""
}

# Check client meets minimum requirements
client_meets_requirements if {
    input.client.dataset_size >= data.enrollment.min_dataset_size
    input.client.cpu_cores >= data.enrollment.min_cpu_cores
    input.client.memory_gb >= data.enrollment.min_memory_gb
}

# Cache client blacklist lookups
#client_blacklisted := cached_blacklist[input.client.id]
#
#cached_blacklist[client_id] := true if {
#    client_id := data.blacklist.client_ids[_]
#}

# Check if client is blacklisted
client_blacklisted if {
    input.client.id in data.blacklist.client_ids
}

# Check if enrollment is open
enrollment_window_open if {
    current_time := time.now_ns()
    current_time >= data.enrollment.start_time
    current_time <= data.enrollment.end_time
}

# Additional info for audit
enrollment_decision := {
    "allowed": allow,
    "client_id": input.client.id,
    "timestamp": time.now_ns(),
    "reasons": reasons
}

reasons contains "authenticated" if client_authenticated
reasons contains "meets_requirements" if client_meets_requirements
reasons contains "blacklisted" if client_blacklisted
reasons contains "window_closed" if not enrollment_window_open