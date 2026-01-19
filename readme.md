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
- **AI (`api/`)**:
    - `api/`: Clients for Anthropic, OpenAI, and Qdrant, including document vectorization and semantic search.
- **Policies & Data (`static/data/`)**: Stores Rego policy files and sample data for onboarding and data format validation.
- **Frontend (`templates/`, `static/`)**: Jinja2 templates and static assets for the web interface.

## OPA server 
 - Instructions to deploy locally: https://www.openpolicyagent.org/docs?current-os=windows#running-opa 
### Run as server
 - opa run --server --set=decision_logs.console=true
 - OPA server is available at http://localhost:8181 

## AI assistant
To be able to get assistance from the LLMs, set the following API keys:
 - ANTHROPIC_API_KEY="sk-ant-api03-..."
 - OPENAI_API_KEY="sk-proj--..."

Optionally, to benefit from RAG and semantic search, set up the QDRANT cluster and provide credentials:
 - QDRANT_URL="..."
 - QDRANT_API_KEY="..."

Optionally, set up the following variables to replace LLM models:
  - ANTHROPIC_MODEL="..."
  - OPENAI_MODEL="..."
