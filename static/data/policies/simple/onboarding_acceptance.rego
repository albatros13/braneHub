package simple.onboarding

# Accepts a participant if their location is within the acceptable locations list.
# Expected input shape:
# {
#   "location": "NL",
#   "acceptable_locations": ["NL", "BE", "DE"]
# }

# Primary boolean decision
default allow = false

allow if {
  # Ensure acceptable_locations is a collection and the location is present in it
  input.acceptable_locations[_] == input.location
}

# Optional convenience object for REST queries that expect an object result
# Query path: /v1/data/simple/onboarding/decision
# Returns: {"allow": true|false}
decision := {"allow": allow}
