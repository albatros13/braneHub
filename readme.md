# Install and run
  - pip install -r requirements.txt
  - flask run
  - the app appears at http://127.0.0.1:5000

## Project Structure & Logical Modules
braneHub is a platform for managing project onboarding with automated policy evaluation.

- **Core Application (`app.py`)**: The main Flask entry point. It handles user authentication, dashboard management, project creation, and the onboarding workflow.
- **OPA Integration (`src/OPAClient.py`)**: Manages communication with the Open Policy Agent (OPA) server. It evaluates onboarding requests against Rego policies.
- **Domain Services (`src/services/`)**:
    - `data_format.py`: Logic for validating and formatting project-specific data requirements.
    - `onboarding.py`: Handles the core onboarding logic and state management.
- **AI & Vector Search (`api/`, `src/`)**:
    - `api/`: Clients for Anthropic, OpenAI, and Qdrant.
    - `src/vectorize*.py`: Scripts for document vectorization and preparation for semantic search.
- **Policies & Data (`static/data/`)**: Stores Rego policy files and sample data for onboarding and data format validation.
- **Frontend (`templates/`, `static/`)**: Jinja2 templates and static assets for the web interface.

## OPA server 
 - Instructions to deploy locally: https://www.openpolicyagent.org/docs?current-os=windows#running-opa 
### Run as server
 - opa run --server --set=decision_logs.console=true
 - OPA server is available at http://localhost:8181 