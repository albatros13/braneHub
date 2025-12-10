package fl.onboarding

# Public decision document returned by the policy engine.
# Usage: opa eval -i input.json "data.fl.onboarding.decision"
default decision = {
    "allow_participation": false,
    "deny_reasons": [],
    "requirements": [],
    "notes": []
}

# Top-level decision construction
decision = {
    "allow_participation": allow,
    "deny_reasons": deny_reasons,
    "requirements": requirements,
    "notes": notes
} {
    allow := count(deny_reasons) == 0
    deny_reasons := collect_denies(input)
    requirements := collect_requirements(input)
    notes := collect_notes(input)
}

########################
# Deny / Hard-fail rules
########################

# Collect explicit deny reasons (hard constraints that block participation)
collect_denies(inp) = reasons {
    reasons := array.concat(
        maybe_irb_block(inp),
        maybe_identifiable_block(inp),
        maybe_network_block(inp)
    )
}

# If IRB/Ethics required and missing -> deny
maybe_irb_block(inp) = [
    "Missing IRB/Ethics approval for human subject data"
] {
    contains_human_data(inp)
    not has_irb_approval(inp)
}

# If dataset contains direct identifiers and provider cannot pseudonymize/anonymize -> deny
maybe_identifiable_block(inp) = [
    "Dataset contains direct identifiers and is not pseudonymized/anonymized"
] {
    inp.identifiability.directIdentifiers == true
    inp.identifiability.processingLevel != "Anonymized"
    inp.identifiability.processingLevel != "Pseudonymized"
    # provider did not claim anonymization or pseudonymization
}

# If outbound networking is completely prohibited and the FL architecture requires outbound comms -> deny
maybe_network_block(inp) = [
    "Outbound network not permitted for required federated communication"
] {
    requires_outbound_comm()
    net := inp.securityInfrastructure.networkConnectionPolicy
    net == "No"
}

########################
# Requirements / mitigations
########################

collect_requirements(inp) = reqs {
    reqs := concat_arrays([
        require_dp_for_sensitive(inp),
        require_encryption_for_model_updates(inp),
        require_per_round_approval(inp),
        require_audit_logging(inp),
        require_data_sharing_agreement(inp),
        require_machine_unlearning_support(inp)
    ])
}

# If quasi-identifiers are present -> require DP or stronger protections
require_dp_for_sensitive(inp) = arr {
    arr = ["Apply differential privacy to model updates before export"]
} {
    inp.identifiability.quasiIdentifiers == true
    # only if provider is not already fully anonymized
    inp.identifiability.processingLevel != "Anonymized"
}

# If provider said only encrypted updates allowed -> enforce encryption
require_encryption_for_model_updates(inp) = arr {
    arr = ["Encrypt model updates (e.g., secure aggregation / TLS + payload encryption)"]
} {
    inp.dataGovernance.modelUpdatesAllowed == "AfterEncryption"
}

# If provider requires per-round approval
require_per_round_approval(inp) = arr {
    arr = ["Require explicit approval from provider before each training round"]
} {
    inp.dataGovernance.requiresPerRoundApproval == true
}

# If provider requires audit logging
require_audit_logging(inp) = arr {
    arr = ["Enable tamper-evident audit logging and provide access to logs"]
} {
    inp.securityInfrastructure.auditLoggingRequired == "Yes"
}

# If agreements are missing -> require DSA/DUA
require_data_sharing_agreement(inp) = arr {
    arr = ["Establish Data Sharing Agreement (DSA) or MOU covering FL participation"]
} {
    not inp.dataGovernance.agreementsExist
}

# If provider expects unlearning on revocation -> require machine unlearning capability or exclusion
require_machine_unlearning_support(inp) = arr {
    arr = ["Support for machine-unlearning or exclusion from future rounds on consent revocation"]
} {
    inp.retentionRevocation.requiresUnlearning == "Yes"
}

########################
# Notes / informational recommendations
########################

collect_notes(inp) = notes {
    notes := concat_arrays([
        note_infrastructure(inp),
        note_certifications(inp),
        note_consent_clarity(inp)
    ])
}

note_infrastructure(inp) = arr {
    arr = ["Confirm runtime and orchestration details: node image, ports, resource limits, upgrade policy"]
} {
    true
}

note_certifications(inp) = arr {
    arr = ["Validate stated certifications (ISO27001/HIPAA/SOC2) via attestation documents"]
} {
    count(inp.securityInfrastructure.securityCertifications) > 0
}

note_consent_clarity(inp) = arr {
    arr = ["If consent is 'Unsure', request legal review of consent language for FL compatibility"]
} {
    inp.dataNature.retrospectiveConsent == "Unsure"
}

########################
# Helper / predicate functions
########################

# Helper: does the input indicate human subject data?
contains_human_data(inp) {
    inp.dataNature.involvesHumanResearch == true
}

# Helper: has IRB approval?
has_irb_approval(inp) {
    inp.ethicalLegal.irbApproval == "Yes"
}

# Helper: does the FL architecture require outbound comms?
# This is a constant here; adapt if your architecture supports pull-based designs.
requires_outbound_comm() {
    # Default to true for common FL: nodes must contact coordinator
    true
}

# Utility: concat many arrays into one
concat_arrays(arrs) = a {
    a := [x | arr := arrs[_]; x := arr[_]]
}

########################
# Example: named fine-grained permit rules (optional)
# These can be used for incremental checks or to produce more structured obligations.
########################

# allow if no hard denies
allow = true {
    count(collect_denies(input)) == 0
}

allow = false {
    count(collect_denies(input)) > 0
}
