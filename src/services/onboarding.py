import json
import os
from typing import Any, Dict, Tuple


def _flatten_input_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten payload['input'] if present, otherwise return payload.get('answers', {})."""
    try:
        if isinstance(payload.get('input'), dict):
            out: Dict[str, Any] = {}
            def flatten(prefix: str, obj: Any):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        flatten(f"{prefix}.{k}" if prefix else k, v)
                else:
                    out[prefix] = obj
            flatten('', payload.get('input'))
            return out
        return payload.get('answers', {}) or {}
    except Exception:
        return {}


def load_flat_answers_for_request(rec: Dict[str, Any], base_dir: str) -> Tuple[Dict[str, Any], str]:
    """Load and flatten the questionnaire answers for a request.
    Returns (flat_answers, rel_path or None).
    """
    answers: Dict[str, Any] = {}
    rel_path = rec.get('answers_file')
    if not rel_path:
        return answers, None
    try:
        abs_path = os.path.join(base_dir, rel_path.replace('/', os.sep))
        with open(abs_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        answers = _flatten_input_payload(payload)
        return answers, rel_path
    except Exception:
        return {}, rel_path


def _to_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ('yes', 'true', 'y', '1'): return True
        if s in ('no', 'false', 'n', '0'): return False
    return False


def _first_nonempty(*vals: Any, default=None):
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == '':
            continue
        return v
    return default


def build_onboarding_opa_input(rec: Dict[str, Any], proj: Dict[str, Any], base_dir: str) -> Dict[str, Any]:
    """Compose OPA input for onboarding.rego from questionnaire answers.
    This is best-effort mapping using common key names; defaults applied when missing.
    """
    flat, _ = load_flat_answers_for_request(rec, base_dir)

    # Try multiple possible keys for each field
    get = flat.get

    input_obj: Dict[str, Any] = {
        'dataNature': {
            'involvesHumanResearch': _to_bool(_first_nonempty(
                get('dataNature.involvesHumanResearch'),
                get('human.involves'),
                get('data.human_subjects')
            )),
            'retrospectiveConsent': _first_nonempty(
                get('dataNature.retrospectiveConsent'),
                get('consent.retrospective'),
                get('consent.status'),
                default='Unknown'
            )
        },
        'ethicalLegal': {
            'irbApproval': _first_nonempty(
                get('ethicalLegal.irbApproval'),
                get('ethics.irb_approval'),
                get('irb.approval'),
                default='No'
            )
        },
        'identifiability': {
            'directIdentifiers': _to_bool(_first_nonempty(
                get('identifiability.directIdentifiers'),
                get('pii.direct_identifiers'),
                get('identifiers.direct')
            )),
            'quasiIdentifiers': _to_bool(_first_nonempty(
                get('identifiability.quasiIdentifiers'),
                get('pii.quasi_identifiers'),
                get('identifiers.quasi')
            )),
            'processingLevel': _first_nonempty(
                get('identifiability.processingLevel'),
                get('privacy.processing_level'),
                get('data.processing_level'),
                default='Raw'
            )
        },
        'dataGovernance': {
            'modelUpdatesAllowed': _first_nonempty(
                get('dataGovernance.modelUpdatesAllowed'),
                get('governance.model_updates'),
                default='AfterEncryption'
            ),
            'requiresPerRoundApproval': _to_bool(_first_nonempty(
                get('dataGovernance.requiresPerRoundApproval'),
                get('governance.per_round_approval')
            )),
            'agreementsExist': _to_bool(_first_nonempty(
                get('dataGovernance.agreementsExist'),
                get('agreements.exist'),
                get('legal.agreements_exist')
            )),
        },
        'securityInfrastructure': {
            'auditLoggingRequired': _first_nonempty(
                get('securityInfrastructure.auditLoggingRequired'),
                get('security.audit_logging_required'),
                default='No'
            ),
            'networkConnectionPolicy': _first_nonempty(
                get('securityInfrastructure.networkConnectionPolicy'),
                get('security.network_connection_policy'),
                default='Yes'
            ),
            'securityCertifications': (
                get('securityInfrastructure.securityCertifications')
                or get('security.certifications')
                or []
            )
        },
        'retentionRevocation': {
            'requiresUnlearning': _first_nonempty(
                get('retentionRevocation.requiresUnlearning'),
                get('retention.requires_unlearning'),
                default='No'
            )
        },
        '_context': {
            'project_id': rec.get('project_id'),
            'applicant': rec.get('username'),
            'project_owner': proj.get('owner')
        }
    }

    # Normalize some enums to expected canonical values
    def norm_yes_no(val):
        if isinstance(val, str):
            s = val.strip().lower()
            if s in ('yes','y','true','1'): return 'Yes'
            if s in ('no','n','false','0'): return 'No'
        return val

    input_obj['ethicalLegal']['irbApproval'] = norm_yes_no(input_obj['ethicalLegal']['irbApproval'])
    input_obj['securityInfrastructure']['auditLoggingRequired'] = norm_yes_no(input_obj['securityInfrastructure']['auditLoggingRequired'])
    input_obj['retentionRevocation']['requiresUnlearning'] = norm_yes_no(input_obj['retentionRevocation']['requiresUnlearning'])

    return input_obj
