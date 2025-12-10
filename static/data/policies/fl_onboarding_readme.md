# Extending the Template

The template is intentionally modular and can be adapted for your federated learning environment.

## 1. Add jurisdiction-specific rules

Use fields like `input.organization.jurisdictions` to implement:
- GDPR constraints (EU)
- HIPAA constraints (US)
- Handling of minors (UK, EU)
- National health-data export laws

## 2. Make FL architecture configurable

Modify the helper predicate `requires_outbound_comm()` to rely on a configuration flag such as:

```json
{
  "flArchitecture": {
    "requiresOutbound": true
  }
}
```

## 3. Add structured obligations

Instead of plain strings in requirements, use structured objects:

```json
{
  "id": "require_dp",
  "severity": "high",
  "params": { "epsilon": 1.0 }
}
```

Modify the Rego rules to produce such objects for better interoperability with BRANE or orchestration systems.

## 4. Add cryptographic and privacy thresholds

Extend requirements to enforce:
- Minimum differential privacy levels
- Secure aggregation vs. homomorphic encryption
- TLS version or cipher suite constraints
- Hash/pseudonymization algorithm requirements

## 5. Add unit tests

Create `policy_test.rego` and add example cases using OPA’s test framework:

```rego
package fl.onboarding

test_no_irb_denied {
    input := {"dataNature": {"involvesHumanResearch": true},
              "ethicalLegal": {"irbApproval": "No"}}
    deny := data.fl.onboarding.decision.deny_reasons
    deny[reason]
    reason == "Missing IRB/Ethics approval for human subject data"
}
```

