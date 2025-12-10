# Federated Learning Data Provider — Policy Onboarding Document

## 1. Introduction

This document guides organizations through the policy and compliance requirements necessary to participate as a data provider in a federated learning network involving medical patient data. Federated learning allows collaborative model training across multiple institutions while keeping data local.

To ensure ethical, legal, and secure participation, we ask each data provider to complete the following onboarding questionnaire. The information will be used to define data-access policies, validate compliance obligations, and configure federated learning nodes appropriately.

## 2. Organizational & Data Governance Information

### 2.1 Organization Details

- Organization name
- Jurisdiction(s) where the data is stored or processed (EU, UK, US, Other)

### 2.2 Primary Contact for Data Governance

- Name
- Position/Role
- Email
- Phone

### 2.3 Data Protection Officer (if applicable)

- Name
- Role
- Email

## 3. Nature of Data for Federated Processing

### 3.1 Types of Data Provided (select all that apply)

- Electronic Health Records (EHR/EMR)
- Diagnostic imaging (CT, MRI, X-ray, etc.)
- Pathology images
- Genomic or other omics datasets
- Laboratory test results
- Sensor/wearable device data
- Claims or administrative billing data
- Other (please specify)

### 3.2 Human Research Context

- Does the dataset involve direct human research? (Yes/No)
- Does it include human biological samples (blood, tissue, cell lines)? (Yes/No)
- If yes, is ethical approval available? (Yes/No)
- Does it include retrospective or preexisting clinical data? (Yes/No)
- Collected with broad consent permitting reuse? (Yes/No/Unsure)

## 4. Identifiability & Data Sensitivity

### 4.1 Personal Data Classification

- Does the dataset contain personal data under GDPR/HIPAA? (Yes/No/Unsure)

### 4.2 Identifiers

- Presence of direct identifiers (name, ID numbers, contact) (Yes/No)
- Presence of quasi-identifiers (DOB, ZIP code, rare diagnosis) (Yes/No)

### 4.3 Identifiable Images or Signals

- Does the dataset include inherently identifiable content (face images, voice, full-body scans, clinical photographs, free text)? (Yes/No)
- If yes, describe masking, anonymization, or redaction methods.

### 4.4 Processing Level

- Fully anonymized
- Pseudonymized
- Identifiable raw data
- Other (please specify)

## 5. Ethical Oversight & Legal Basis

### 5.1 Ethics Approval

- Do you have IRB/Ethics Committee approval for federated learning participation? (Yes/No/Not applicable)
- If yes: provide approval ID and issuing body.

### 5.2 Legal Basis for Data Processing

Select all that apply:

- Informed consent
- Broad consent
- Public interest in scientific research
- Legitimate interest
- Contractual obligations
- Other

### 5.3 Consent for Federated Learning

- Does consent explicitly permit federated or distributed analytics? (Yes/No/Not applicable)

### 5.4 Use Restrictions

Please specify any:

- Disease-specific restrictions
- Non-commercial only constraints
- Geographic restrictions
- Other limitations

## 6. Security, Infrastructure & Technical Requirements

### 6.1 Hosting Environment

Where will your federated learning node run?

- On-premise servers
- Private cloud
- Public cloud
- Hospital secure enclave
- Other

### 6.2 Security Certifications

Select any that apply:

- ISO 27001
- HIPAA compliance
- NEN 7510
- SOC 2
- None
- Other certifications

### 6.3 Access Control Requirements

Preferred model:

- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)
- Consent-aware access control
- Policy-based control (XACML/Rego/OPA)
- Unsure

### 6.4 Logging & Auditability

- Do you require audit logging of model requests or parameters exchanged?
  - Yes
  - No
  - Conditional

### 6.5 Network Policies

Outbound network traffic allowed?

- Yes
- No
- Only via proxy
- Only via VPN
- Other restrictions (please specify)

## 7. Data Governance Constraints

### 7.1 Institutional Agreements

- Are data-sharing agreements, MTAs, DUAs, or internal policies in place that impose constraints? (Yes/No)
- If yes, attach or describe relevant clauses.

### 7.2 Restrictions on Model Updates

Can model updates derived from your data leave your environment?

- Yes
- Only after differential privacy
- Only after encryption
- No

### 7.3 Training Approval

- Do you require approval for each training round or model update? (Yes/No)

### 7.4 Restricted Data Categories

- List any data categories that must not be used in model training (e.g., minors, psychiatric records, genetic profiles).

## 8. Retention, Revocation & Data Subject Rights

### 8.1 Consent Revocation

- Can participants revoke consent for research use? (Yes/No/Unknown)

### 8.2 Machine Unlearning Requirements

If revocation occurs, is machine unlearning required?

- Yes
- No
- Case-by-case

### 8.3 Retention Period

- Specify required data retention period.

## 9. Additional Notes

Use this section to provide any further ethical, legal, technical, or organizational constraints relevant to federated learning participation.

## 10. Submission

Please return the completed document along with any supporting documentation (ethics approval, consent forms, data-sharing agreements, infrastructure descriptions, etc.) to the study coordination team.