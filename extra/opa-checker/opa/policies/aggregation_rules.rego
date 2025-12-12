package federated.aggregation

import future.keywords.if
import future.keywords.in

default allow_aggregation := false

# Allow aggregation if conditions met
allow_aggregation if {
    minimum_participants_met
    data_quality_sufficient
    privacy_budget_available
}

# Check minimum number of participants
minimum_participants_met if {
    count(input.participants) >= data.aggregation.min_participants
}

# Check data quality across participants
data_quality_sufficient if {
    total_samples := sum([p.num_samples | p := input.participants[_]])
    total_samples >= data.aggregation.min_total_samples

    # All participants must have minimum samples
    all_have_min_samples
}

all_have_min_samples if {
    every participant in input.participants {
        participant.num_samples >= data.aggregation.min_samples_per_client
    }
}

# Check privacy budget (differential privacy)
privacy_budget_available if {
    current_epsilon := data.privacy.current_epsilon_spent
    epsilon_for_round := input.round.epsilon_cost
    total_epsilon := current_epsilon + epsilon_for_round

    total_epsilon <= data.privacy.max_epsilon_budget
}

# Aggregation decision with details
aggregation_decision := {
    "allowed": allow_aggregation,
    "round": input.round.number,
    "num_participants": count(input.participants),
    "total_samples": sum([p.num_samples | p := input.participants[_]]),
    "privacy_budget_remaining": data.privacy.max_epsilon_budget - data.privacy.current_epsilon_spent,
    "reasons": denial_reasons
}

denial_reasons contains "insufficient_participants" if not minimum_participants_met
denial_reasons contains "insufficient_data_quality" if not data_quality_sufficient
denial_reasons contains "privacy_budget_exhausted" if not privacy_budget_available