# Data Format and Representation Overview

This guide helps teams explain how data is stored inside their organization, how its structure is described (schemas/contracts), and how to share these representations safely with collaborators. It is meant to be copy-paste friendly and applicable across research, healthcare, and analytics settings.

Updated: 2025-12-12


## Why this matters
- Makes integration predictable: consumers know types, shapes, and constraints.
- Reduces risk: governance, privacy, and consent constraints are explicit.
- Enables automation: contracts (JSON Schema, OpenAPI, Avro/Protobuf) can be validated in CI and used to generate code and documentation.


## How organizations store data (storage patterns)
Consider which of these apply to your datasets. You can select more than one.

- Files (batch)
  - CSV/TSV, Excel (XLSX)
  - JSON, NDJSON/JSONL, XML, YAML
  - Columnar analytics: Parquet, ORC, Arrow/Feather, Delta
  - Scientific/binary: HDF5, NetCDF, DICOM, NIfTI
  - Domain: FASTA/VCF/BAM (genomics), HL7 v2, FHIR bundles (NDJSON), DICOM
- Databases
  - Relational: PostgreSQL, MySQL/MariaDB, SQL Server, Oracle
  - Analytical warehouses/lakes: BigQuery, Snowflake, Redshift, Lakehouse
  - NoSQL: MongoDB, Cassandra, Elasticsearch, Neo4j (graphs)
- APIs and streams
  - REST/HTTP, GraphQL
  - Event/streaming: Kafka, Pulsar, Kinesis; message formats often Avro/Protobuf
- Object storage
  - S3, GCS, Azure Blob, on‑prem object stores (MinIO, Ceph)


## ✅ Canonical Source of Truth (SoT)
The **SoT** is the single, authoritative place where data is defined and maintained.  
It is the version that everyone agrees is correct and complete.

**Examples:**
- A master database table  
- A Git repository for configuration files  
- A central data warehouse  
- A primary API that owns the data model  

---

### ✅ Downstream Exports
Downstream exports are **copies, subsets, or transformed versions** of the SoT, created for specific uses.

**Examples:**
- CSV exports for reporting  
- Cached or reduced datasets for analytics  
- Replicas or materialized views  
- Shared folders or files used across teams  
- API responses that expose a subset of fields  

---

### Why this matters
When documenting or designing a workflow, explicitly identify:

1. **Where the authoritative version lives** (the SoT)  
2. **Where the data flows afterward** (downstream exports)  
3. **Who uses the exported versions and for what**  

Doing this helps avoid:
- Conflicting versions of data  
- Out-of-date datasets  
- Teams modifying the wrong copy 


## How data structure is described (schemas/contracts)
Choose one or more approaches to describe your datasets precisely.

- JSON & API contracts
  - JSON Schema (field types, required, enums, patterns)
  - OpenAPI/Swagger (endpoints + request/response schemas)
  - GraphQL schema (types, queries, relations)
- XML
  - XML Schema (XSD), DTD (legacy)
- Streaming/binary
  - Avro schema (great for schema evolution)
  - Protocol Buffers (.proto) and gRPC service definitions
  - Thrift IDL (less common now)
- Databases
  - SQL DDL (CREATE TABLE …), constraints, indexes
  - ER diagrams and data dictionaries
- Semantic/metadata standards
  - RDF/OWL, SHACL constraints, JSON‑LD (FAIR/linked data)

Recommendation: version your schemas (e.g., semver tags v1.2.0) and maintain a change log describing breaking vs. non‑breaking changes.


## Governance and metadata to include
Provide metadata so consumers can correctly interpret your data and obligations.

- Business glossary and field descriptions
- Allowed values/enumerations and units of measurement
- Time handling (ISO 8601 timestamps, time zones)
- Data provenance (source system, extract date, cohort criteria)
- Quality rules (nullability, ranges, primary keys, uniqueness)
- Versioning policy (how schemas evolve; deprecation windows)
- Privacy/legal constraints (identifiability, consent scope, IRB/REC status)


## Sharing representations inside and outside your organization
Document where people can find and trust your formats and schemas.

- Source control
  - Keep schemas and example payloads in a Git repository (e.g., schemas/ directory)
  - Use PR reviews and CI validation (e.g., validate JSON files against JSON Schema)
- Catalogs and registries
  - Data catalogs (DataHub, Collibra, Amundsen) for discoverability
  - Schema registries (Confluent, AWS Glue) for streams and tables
- Documentation portals
  - Publish API specs (OpenAPI/GraphQL) and ERDs on an internal docs site
- Access governance
  - Define owners, approvers, and contact emails
  - Specify permitted uses, licenses, and retention/revocation rules

For external sharing, provide:
- Versioned schema files (e.g., JSON Schema, .proto, Avro .avsc)
- Example files/samples (small, de‑identified where applicable)
- An “Integration Guide” describing endpoints, auth, pagination, error shapes, and rate limits.


## Minimal questionnaire for data providers
You can use the following checklist to collect consistent information from data providers.

1) Storage format(s)
- [ ] CSV/TSV
- [ ] Excel (XLSX)
- [ ] JSON / NDJSON
- [ ] XML / YAML
- [ ] Parquet / ORC / Arrow / Delta
- [ ] Avro / Protobuf
- [ ] Database export (type: ____________)
- [ ] Stream (Kafka/Pulsar topic: ____________)
- [ ] Other: _______________________

2) Schema/structure description
- [ ] JSON Schema
- [ ] OpenAPI/Swagger
- [ ] GraphQL schema
- [ ] XML Schema (XSD)
- [ ] Avro schema
- [ ] Protobuf (.proto)
- [ ] SQL DDL / ER diagram
- [ ] Data dictionary
- [ ] Other: _______________________

3) Metadata and governance
- [ ] Field descriptions / glossary
- [ ] Allowed values / units
- [ ] Timestamps and time zone conventions
- [ ] Data provenance / source systems
- [ ] Versioning policy (schema evolution)
- [ ] Data quality rules / constraints
- [ ] Privacy/legal notes (consent, IRB/REC, identifiability)

4) Access & delivery
- [ ] Downloadable files (format: ____________)
- [ ] API endpoints (REST/GraphQL) — attach spec
- [ ] Database connection (credentials required)
- [ ] Object store path (e.g., s3://bucket/prefix)
- [ ] Streaming (topic name, schema, retention)
- [ ] Other: _______________________

5) Operational details
- [ ] Update cadence (e.g., nightly, weekly)
- [ ] Size per delivery and total history
- [ ] Expected error rates and retries
- [ ] Contact for incidents/changes


## Examples (brief)

- CSV + JSON Schema
  - data/patients.csv
  - schemas/patients.schema.json (defines types, required columns, enums)
- Parquet in S3 + Glue catalog
  - s3://org-analytics/ehr/encounters/ (Parquet), schema tracked in AWS Glue and DataHub
- API with OpenAPI
  - GET /v1/encounters/{id} described in openapi.yaml; example responses stored under examples/
- Streaming with Avro
  - Kafka topic ehr.encounter.v2 with Avro schema in Confluent Schema Registry


## Using this in BraneHub
- Attach questionnaire/spec content to the AI Assistant from relevant pages (Include in AI context).
- Ask the Assistant to generate or validate schemas and integration guides.
- When the model returns a file (e.g., patients.schema.json or openapi.yaml), use the Review modal to save it. Files are saved under static/data/artifacts.


## Request email template
Subject: Request for Data Format, Schema, and Metadata

Dear [Name/Team],

To integrate the dataset(s) you plan to share, please provide the storage format(s), schema/contract, and key metadata. You may attach existing documents or complete the checklist below.

- Storage format(s): [CSV/Parquet/JSON/API/DB/Stream/Other]
- Schema/contract: [JSON Schema/OpenAPI/DDL/Avro/Protobuf/ERD/Data Dictionary]
- Access method: [Download/API/DB/Stream/Object Store]
- Versioning: [Semver tag, registry/catalog link]
- Samples: [Small redacted files or example payloads]
- Governance: [Owners, permitted uses, consent/IRB notes]

Thank you,
[Your name] / [Team]
