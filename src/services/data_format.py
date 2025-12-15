import json
import os
from typing import Any, Dict


def _to_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, str) and v.strip() == "":
        return []
    return [v]


def has_data_answers_for_request(rec: Dict[str, Any], base_dir: str) -> bool:
    """Detect whether applicant provided data-format answers for a request.
    - Checks explicit `data_answers_file` path if present.
    - Falls back to scanning static/data/db/data_format_answers for the latest file
      that matches the pattern: "{project_id}_{username}_*.json".
    """
    try:
        df_abs_path = None
        linked_rel = rec.get('data_answers_file')
        if linked_rel:
            df_abs_path = os.path.join(base_dir, linked_rel.replace('/', os.sep))
        if df_abs_path and os.path.isfile(df_abs_path):
            return True
        df_dir = os.path.join(base_dir, 'static', 'data', 'db', 'data_format_answers')
        if os.path.isdir(df_dir):
            prefix = f"{rec.get('project_id')}_{rec.get('username')}_"
            files = [f for f in os.listdir(df_dir) if f.startswith(prefix) and f.endswith('.json')]
            if files:
                return True
    except Exception:
        pass
    return False


def load_expected(owner: str, base_dir: str) -> Dict[str, Any]:
    """Load the most recent data-format expectations JSON for an owner.
    Returns a normalized dict structure suitable for OPA input.
    """
    exp_dir = os.path.join(base_dir, 'static', 'data', 'db', 'data_format_expectations')
    expected = {"storage": {}, "schema": {"contracts": {}}, "delivery": {}}
    try:
        if os.path.isdir(exp_dir):
            files = [f for f in os.listdir(exp_dir) if f.startswith(f"owner_{owner}_") and f.endswith('.json')]
            if files:
                files.sort(reverse=True)
                with open(os.path.join(exp_dir, files[0]), 'r', encoding='utf-8') as f:
                    exp_payload = json.load(f)
                    exp_struct = exp_payload.get('expectations') or {}
                    expected = {
                        "storage": {
                            k: {
                                "acceptable": _to_list((exp_struct.get('storage', {}).get(k, {}) or {}).get('acceptable')),
                                "conditional": _to_list((exp_struct.get('storage', {}).get(k, {}) or {}).get('conditional')),
                                "not_acceptable": _to_list((exp_struct.get('storage', {}).get(k, {}) or {}).get('not_acceptable')),
                            } for k in ['files', 'databases', 'apis_streams', 'object_store']
                        },
                        "schema": {
                            "contracts": {
                                "acceptable": _to_list((exp_struct.get('schema', {}).get('contracts', {}) or {}).get('acceptable')),
                                "conditional": _to_list((exp_struct.get('schema', {}).get('contracts', {}) or {}).get('conditional')),
                                "not_acceptable": _to_list((exp_struct.get('schema', {}).get('contracts', {}) or {}).get('not_acceptable')),
                            }
                        },
                        "delivery": {
                            "methods": {
                                "acceptable": _to_list((exp_struct.get('delivery', {}).get('methods', {}) or {}).get('acceptable')),
                                "conditional": _to_list((exp_struct.get('delivery', {}).get('methods', {}) or {}).get('conditional')),
                                "not_acceptable": _to_list((exp_struct.get('delivery', {}).get('methods', {}) or {}).get('not_acceptable')),
                            }
                        },
                        "meta": exp_struct.get('meta', {})
                    }
    except Exception:
        expected = {"storage": {}, "schema": {"contracts": {}}, "delivery": {}}
    return expected


def load_provided(rec: Dict[str, Any], base_dir: str) -> Dict[str, Any]:
    """Load the applicant-provided data-format answers for a request.
    Uses explicit path in the record if present, otherwise picks the latest file by pattern.
    Returns normalized dict for OPA input.
    """
    provided = {"storage": {}, "schema": {}, "meta": {}, "delivery": {}, "ops": {}}
    try:
        df_abs_path = None
        linked_rel = rec.get('data_answers_file')
        if linked_rel:
            df_abs_path = os.path.join(base_dir, linked_rel.replace('/', os.sep))
        if not df_abs_path or not os.path.isfile(df_abs_path):
            df_dir = os.path.join(base_dir, 'static', 'data', 'db', 'data_format_answers')
            if os.path.isdir(df_dir):
                prefix = f"{rec.get('project_id')}_{rec.get('username')}_"
                files = [f for f in os.listdir(df_dir) if f.startswith(prefix) and f.endswith('.json')]
                if files:
                    files.sort(reverse=True)
                    df_abs_path = os.path.join(df_dir, files[0])
        if df_abs_path and os.path.isfile(df_abs_path):
            with open(df_abs_path, 'r', encoding='utf-8') as f:
                df_payload = json.load(f)
                structured = (df_payload.get('data_format') or {})
                st = structured.get('storage', {})
                provided['storage'] = {
                    'files': _to_list(st.get('files')),
                    'databases': _to_list(st.get('databases')),
                    'apis_streams': _to_list(st.get('apis_streams')),
                    'object_store': _to_list(st.get('object_store')),
                    'source_of_truth': (st.get('source_of_truth') or None)
                }
                sch = structured.get('schema', {})
                for key in ['json_schema','openapi','graphql','xml_xsd','avro','protobuf','sql_ddl','data_dictionary','other']:
                    val = sch.get(key)
                    if val is None:
                        continue
                    provided['schema'][key] = val
                meta = structured.get('meta', {})
                for key in ['field_descriptions','allowed_values_units','time_handling','provenance','quality_rules','versioning_policy','privacy_legal']:
                    val = meta.get(key)
                    if val is None:
                        continue
                    provided['meta'][key] = val
                deliv = structured.get('delivery', {})
                provided['delivery'] = {
                    'methods': _to_list(deliv.get('methods')),
                    'files_format': deliv.get('files_format') or None,
                    'api_spec': deliv.get('api_spec') or None,
                    'db_details': deliv.get('db_details') or None,
                    'object_store_path': deliv.get('object_store_path') or None,
                    'stream_details': deliv.get('stream_details') or None,
                }
                ops = structured.get('ops', {})
                provided['ops'] = {
                    'update_cadence': ops.get('update_cadence') or None,
                    'size_profile': ops.get('size_profile') or None,
                    'error_retries': ops.get('error_retries') or None,
                    'contact': ops.get('contact') or None,
                }
    except Exception:
        provided = {"storage": {}, "schema": {}, "meta": {}, "delivery": {}, "ops": {}}
    return provided


def build_opa_input_for_request(rec: Dict[str, Any], proj: Dict[str, Any], base_dir: str) -> Dict[str, Any]:
    """Compose the OPA input payload for the given onboarding request and project."""
    expected = load_expected(proj.get('owner'), base_dir)
    provided = load_provided(rec, base_dir)
    opa_input = {
        'expected': expected,
        'provided': provided,
        '_context': {
            'project_id': rec.get('project_id'),
            'applicant': rec.get('username'),
        }
    }
    return opa_input
