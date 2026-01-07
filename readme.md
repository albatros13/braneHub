# Install and run
  - pip install -r requirements.txt
  - flask run
  - the app appears at http://127.0.0.1:5000
## OPA server 
 - Instructions to deploy locally: https://www.openpolicyagent.org/docs?current-os=windows#running-opa 
### Run as server
 - opa run --server --set=decision_logs.console=true
 - OPA server is available at http://localhost:8181 