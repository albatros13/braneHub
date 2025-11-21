import yaml
from pathlib import Path

def convert_arazzo_to_federated_yaml(arazzo_spec, output_dir=".", generate_policy=True):
    """
    Convert an Arazzo workflow specification (Python dict) into
    a federated YAML job spec compatible with a federated node runtime.

    Parameters
    ----------
    arazzo_spec : dict
        Parsed Arazzo YAML specification (as a Python dictionary).
    output_dir : str, optional
        Directory where the generated YAML files will be stored.
    generate_policy : bool, optional
        Whether to produce a separate policy.yaml file for OPA enforcement.

    Returns
    -------
    dict
        The federated workflow specification (as a Python dict).
    """
    workflows = arazzo_spec.get("workflows", {})
    x_policy = arazzo_spec.get("x-policy", {})

    generated_policies = []  # for optional OPA file output

    for wf_name, wf_def in workflows.items():
        federated = {
            "name": wf_name,
            "version": arazzo_spec.get("info", {}).get("version", "1.0"),
            "description": wf_def.get("description", "Federated workflow"),
            "inputs": {},
            "steps": [],
            "outputs": {},
        }

        # Map inputs
        for inp_name, inp_def in wf_def.get("inputs", {}).items():
            federated["inputs"][inp_name] = {
                "type": inp_def.get("type", "File"),
                "description": inp_def.get("description", "")
            }

        # Map outputs
        for out_name, out_def in wf_def.get("outputs", {}).items():
            federated["outputs"][out_name] = {
                "type": out_def.get("type", "File"),
                "description": out_def.get("description", "")
            }

        # Map steps
        for step in wf_def.get("steps", []):
            step_yaml = {
                "id": step["id"],
                "name": step["name"],
                "command": ["python", "pipeline.py", step["operationId"]],
            }

            # Inputs
            if "inputs" in step:
                step_yaml["inputs"] = list(step["inputs"].keys())

            # Outputs
            if "outputs" in step:
                outputs = step["outputs"]
                if isinstance(outputs, dict):
                    step_yaml["outputs"] = list(outputs.keys())
                elif isinstance(outputs, list):
                    step_yaml["outputs"] = outputs

            # Error handling
            if "onError" in step:
                step_yaml["onError"] = {"action": "fail"}
                if "next" in step["onError"]:
                    step_yaml["onError"]["next"] = step["onError"]["next"]

            # Compliance annotations
            if "x-compliance" in step:
                rules = step["x-compliance"].get("rules", [])
                step_yaml["annotations"] = {
                    "compliance": [
                        {
                            "id": r.get("id"),
                            "type": r.get("type"),
                            "requirement": r.get("requirement"),
                            "article": r.get("article"),
                            "verifiedBy": r.get("verifiedBy"),
                            "enforcement": r.get("enforcement"),
                            "description": r.get("description"),
                        }
                        for r in rules
                    ]
                }

                # Add to policy manifest if requested
                if generate_policy:
                    for r in rules:
                        generated_policies.append({
                            "step": step["id"],
                            "policy_id": r.get("id"),
                            "article": r.get("article"),
                            "requirement": r.get("requirement"),
                            "verifiedBy": r.get("verifiedBy"),
                            "enforcement": r.get("enforcement"),
                        })

            federated["steps"].append(step_yaml)

        # Write YAML outputs
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        wf_path = output_dir / f"{wf_name}.yaml"

        with wf_path.open("w") as f:
            yaml.dump(federated, f, sort_keys=False)

        print(f"✅ Federated workflow written to: {wf_path}")

        # Optionally write OPA policy manifest
        if generate_policy and generated_policies:
            policy_manifest = {
                "engine": x_policy.get("engine", "opa"),
                "policyRefs": x_policy.get("policyRefs", []),
                "rules": generated_policies,
            }
            policy_path = output_dir / f"{wf_name}_policy.yaml"
            with policy_path.open("w") as f:
                yaml.dump(policy_manifest, f, sort_keys=False)
            print(f"✅ Policy manifest written to: {policy_path}")

        return federated  # return the generated dict for convenience
