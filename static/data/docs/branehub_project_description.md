BraneHub: An AI‑Assisted Platform for Federated Data Processing Network Setup

Purpose and Motivation
BraneHub accelerates the formation of federated data processing (FDP) collaborations between institutions by unifying onboarding, data‑format negotiation, and policy‑aware decision support in a single, lightweight web application. FDP projects often stall during early coordination: owners must articulate requirements, prospective participants must share capabilities and constraints, and both parties need rapid, transparent feedback on compatibility and compliance. BraneHub addresses this gap by combining structured questionnaires, policy evaluation (via Open Policy Agent, OPA), and an integrated AI assistant to streamline technical and administrative alignment.

Core Functionality
- Project creation and ownership: Researchers define an FDP project, including objectives, data types, sensitivity level, and basic governance parameters. Projects are persisted in a registry and associated with the owner.
- Participant onboarding: Prospective participants submit onboarding requests with two complementary artifacts:
  1) General questionnaire responses (institution, use case, safeguards, etc.)
  2) Data‑format answers describing their local datasets and interfaces
- Owner review workflow: Project owners view per‑request details, inspect questionnaire responses, and take a decision (accept/reject) with optional justification. Accepted users are added to the project’s participant list.
- Data compatibility checks with OPA: BraneHub assembles “expected” (owner‑provided) vs. “provided” (applicant‑provided) data‑format specifications into an OPA input and evaluates a policy to produce an allow/deny outcome along with reasons, requirements, and notes. This formalizes early interoperability checks while remaining explainable and auditable.
- AI‑assisted decision support: An optional AI assistant (OpenAI or Anthropic, with pluggable RAG) can ingest context from forms and policies. Users can attach questionnaire and data‑format snippets directly to the chat to obtain summaries, gap analyses, and drafting support (e.g., onboarding feedback or MoU clauses). Artifacts generated in chat can be saved back to the repository.

System Architecture (high‑level)
- Web application: Flask server with routes for authentication, dashboards, project creation, onboarding requests, and assistant APIs. Templates render owner and participant views.
- Services layer: Data‑format utilities encapsulated in src/services (e.g., assemble OPA inputs and detect answer presence), keeping routes lean and testable.
- Policy evaluation: A lightweight OPA client uploads a purpose‑built Rego policy and evaluates compliance decisions over structured inputs.
- Data and configuration: JSON‑based registries for projects, onboarding requests, questionnaires, and answers. Static policies and schemas live under the repository’s static/data directory for reproducibility.
- AI assistant integration: Provider‑agnostic abstraction supports OpenAI or Anthropic models; optional retrieval augments prompts with domain context. The UI exposes “Include in AI context” buttons to pass relevant JSON directly to the assistant.

Typical Workflow
1) A project owner publishes expected data‑format requirements alongside project metadata.
2) A prospective participant submits onboarding responses and data‑format answers.
3) The owner reviews the request, previews the applicant’s data‑format details, and runs an OPA evaluation to get an allow/deny decision with explanatory reasons.
4) When needed, the owner injects the same context into the AI assistant to obtain human‑readable rationales, discrepancy analyses, or negotiation drafts.
5) The owner accepts or rejects the request; accepted users become project participants.

Design Principles
- Explainability and auditability: Formal OPA decisions are presented with reasons and requirements; AI‑generated guidance is kept separate and optional.
- Minimal friction: All inputs are JSON‑backed and file‑based for portability; no heavyweight orchestration is required for early‑stage coordination.
- Extensibility: Policies, questionnaires, and model providers can be swapped without changing core workflows.

Current Scope and Limitations
- BraneHub focuses on pre‑integration alignment (capabilities, formats, and governance). It does not execute federated analytics or secure computation itself.
- Compliance guidance is advisory; authoritative legal review remains out of scope. OPA policies are examples and should be tailored to institutional standards.

Outlook
Future work includes richer schema catalogs (e.g., FHIR/OMOP profiles), automated conformance validation against sample datasets, policy libraries for cross‑jurisdictional requirements, and integrations with orchestration layers that can translate accepted onboarding decisions into deployable federation configurations.
