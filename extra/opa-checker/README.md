# OPA Deploymnet

## Sidecar container alongside other nodes
 - opa-checker/docker-compose.yml

## Locally deployed 
 - Instructions https://www.openpolicyagent.org/docs?current-os=windows#running-opa 
### Run as server
 - opa run --server --set=decision_logs.console=true
  
## Server-side integration (e.g., Flask in BraneHub)
 - src/OPAClient.py

# Troubleshooting
## Common Issues
### OPA not receiving requests

* Check network connectivity: curl http://localhost:8181/health
* Verify OPA is running: docker ps | grep opa

### Policy evaluation errors

* Test policy syntax: opa check ./policies
* Use OPA playground: https://play.openpolicyagent.org/

### Performance issues

* Enable policy caching
* Use partial evaluation for complex policies
* Profile policies: opa test --profile ./policies