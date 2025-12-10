from flask import Flask, render_template, request, redirect, url_for, session, abort
from functools import wraps
from datetime import datetime
import json
import os

app = Flask(__name__)
# NOTE: Replace this with a secure random value in production
app.secret_key = 'dev-secret-key-change-me'

# In-memory stores initialized from registry file
users = {}  # username -> {password: str}
projects_catalog = []  # list of projects
project_participants = {}  # project_id -> list[usernames]
user_projects = {}  # username -> list[project_id]


def load_registry():
    """Load users, projects, and participants from project_registry.json and
    reconstruct user_projects from project ownership."""
    global users, projects_catalog, project_participants, user_projects
    registry_path = os.path.join(
        os.path.dirname(__file__), 'static', 'data', 'db', 'project_registry.json'
    )
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        # Fallback to empty structures if file missing
        data = {"users": [], "projects": [], "project_participants": {}}

    # Initialize users dict; if passwords aren't present, default to empty string
    users = {u.get('id'): {"password": u.get('password', '')} for u in data.get('users', []) if u.get('id')}

    # Projects and participants directly from registry
    projects_catalog = data.get('projects', [])
    project_participants = data.get('project_participants', {})

    # Reconstruct user_projects from project owners
    user_projects = {}
    for proj in projects_catalog:
        owner = proj.get('owner')
        pid = proj.get('id')
        if owner and pid is not None:
            user_projects.setdefault(owner, []).append(pid)


def save_registry():
    """Persist current in-memory stores to project_registry.json."""
    registry_path = os.path.join(
        os.path.dirname(__file__), 'static', 'data', 'db', 'project_registry.json'
    )
    data = {
        "projects": projects_catalog,
        "project_participants": project_participants,
        "users": [{"id": uname, **({"password": rec.get("password")} if rec.get("password") else {})}
                  for uname, rec in users.items()]
    }
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # Minimal error handling; in real app use logging
        print(f"Warning: failed to save registry: {e}")


# Load data at startup
load_registry()

# --- Onboarding requests helpers ---

def load_onboarding_requests():
    req_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'db', 'onboarding_requests.json')
    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Warning: failed to load onboarding requests: {e}")
        return []


def save_onboarding_requests(records):
    req_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'db', 'onboarding_requests.json')
    try:
        os.makedirs(os.path.dirname(req_path), exist_ok=True)
        with open(req_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: failed to save onboarding requests: {e}")


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapper


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = 'Username and password are required.'
        elif username in users:
            error = 'Username already exists.'
        else:
            users[username] = {"password": password}
            user_projects[username] = []
            session['user'] = username
            return redirect(url_for('dashboard'))
    return render_template('signup.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = users.get(username)
        if not user or user.get('password') != password:
            error = 'Invalid username or password.'
        else:
            session['user'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    username = session['user']
    own_ids = set(user_projects.get(username, [])) | {p_id for p_id, members in project_participants.items() if username in members}
    own_list = [p for p in projects_catalog if p['id'] in own_ids]
    explore_list = [p for p in projects_catalog if p['id'] not in own_ids]
    return render_template('dashboard.html', username=username, own_projects=own_list, explore_projects=explore_list, participants=project_participants)


@app.route('/fdp/new', methods=['GET', 'POST'])
@login_required
def fdp_new():
    username = session['user']
    error = None
    # Predefined options
    data_types_options = ['Imaging', 'EHR', 'Genomics', 'Wearables', 'Lab Results']
    security_measures_options = ['Encryption', 'Secure Containers', 'Access Logs', 'Pseudonymization']
    legal_basis_options = ['GDPR Consent', 'HIPAA TPO', 'Public Interest', 'Research with Waiver']

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        institution = request.form.get('institution', '').strip()
        email = request.form.get('email', '').strip()
        objective = request.form.get('objective', '').strip()
        data_types = request.form.getlist('data_types')  # multi-select
        sensitivity = request.form.get('sensitivity', '').strip()  # radio
        security_measures = request.form.getlist('security_measures')  # checklist
        result_sharing = request.form.get('result_sharing', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()
        legal_basis = request.form.get('legal_basis', '').strip()
        third_party = request.form.get('third_party', 'no').strip()  # yes/no

        # Basic validation
        if not title or not institution or not email or not objective:
            error = 'Title, Research Institution, Contact Email, and Study Objective are required.'
        elif '@' not in email or '.' not in email:
            error = 'Please provide a valid contact email.'
        else:
            # Generate a new string ID like 'projectN'
            def next_project_id(existing_ids):
                max_n = 0
                for pid in existing_ids:
                    if isinstance(pid, str) and pid.lower().startswith('project'):
                        suffix = pid[7:]
                        if suffix.isdigit():
                            max_n = max(max_n, int(suffix))
                return f"project{max_n + 1}" if max_n >= 0 else "project1"

            existing_ids = [p.get('id') for p in projects_catalog]
            new_id = next_project_id(existing_ids)
            project = {
                'id': new_id,
                'title': title,
                'owner': username,
                'tags': ['fdp'] + [t.lower() for t in data_types],
                'type': 'FDP',
                'fdp': {
                    'research_institution': institution,
                    'contact_email': email,
                    'study_objective': objective,
                    'data_types_required': data_types,
                    'data_sensitivity_level': sensitivity or 'Medium',
                    'security_measures_planned': security_measures,
                    'result_sharing_policy': result_sharing,
                    'participant_responsibilities': responsibilities,
                    'legal_basis_for_processing': legal_basis,
                    'third_party_collaboration': True if third_party.lower() == 'yes' else False,
                }
            }
            projects_catalog.append(project)
            # Associate to user
            user_projects.setdefault(username, [])
            if project['id'] not in user_projects[username]:
                user_projects[username].append(project['id'])
            # Make creator a participant
            project_participants.setdefault(project['id'], [])
            if username not in project_participants[project['id']]:
                project_participants[project['id']].append(username)
            # Persist to registry so the new project is saved
            save_registry()
            return redirect(url_for('dashboard'))

    return render_template(
        'fdp_new.html',
        error=error,
        data_types_options=data_types_options,
        security_measures_options=security_measures_options,
        legal_basis_options=legal_basis_options,
    )


@app.route('/join/<project_id>', methods=['POST'])
@login_required
def join_project(project_id):
    # Instead of directly joining, redirect to onboarding questionnaire
    if not any(str(p.get('id')) == str(project_id) for p in projects_catalog):
        return redirect(url_for('dashboard'))
    return redirect(url_for('onboarding', project_id=project_id))


if __name__ == '__main__':
    # Run in debug for development convenience
    app.run(debug=True)



@app.route('/project/<project_id>')
@login_required
def project_manage(project_id):
    # Find project by id
    project = next((p for p in projects_catalog if str(p.get('id')) == str(project_id)), None)
    if not project:
        return redirect(url_for('dashboard'))
    username = session['user']
    is_owner = (project.get('owner') == username)
    participants = project_participants.get(project_id, [])

    # Load onboarding requests for this project (owner-only view)
    project_reqs = []
    if is_owner:
        all_reqs = load_onboarding_requests()
        for idx, rec in enumerate(all_reqs):
            if str(rec.get('project_id')) != str(project_id):
                continue
            project_reqs.append({
                **rec,
                '_id': idx,
            })
        # Sort: pending first, then by submitted_at desc
        def sort_key(r):
            pri = {'submitted': 0, 'accepted': 1, 'rejected': 1}.get(r.get('status', 'submitted'), 1)
            return (pri, r.get('submitted_at', ''),)
        project_reqs.sort(key=lambda r: ( {'submitted':0,'accepted':1,'rejected':1}.get(r.get('status','submitted'),1), r.get('submitted_at','') ), reverse=False)

    return render_template('project_manage.html', project=project, participants=participants, is_owner=is_owner, project_requests=project_reqs)


@app.route('/onboarding/<project_id>', methods=['GET', 'POST'])
@login_required
def onboarding(project_id):
    # Ensure project exists
    project = next((p for p in projects_catalog if str(p.get('id')) == str(project_id)), None)
    if not project:
        return redirect(url_for('dashboard'))

    # Load questionnaire definition
    q_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'policies', 'fl_onboarding_questionnaire.json')
    try:
        with open(q_path, 'r', encoding='utf-8') as f:
            questionnaire = json.load(f)
    except Exception as e:
        questionnaire = {"title": "Onboarding Questionnaire", "sections": []}

    error = None
    if request.method == 'POST':
        # Collect answers from the posted form
        answers = {}
        for section in questionnaire.get('sections', []):
            for q in section.get('questions', []):
                qid = q.get('id')
                qtype = q.get('type')
                if not qid:
                    continue
                form_key = qid.replace('.', '__')
                if qtype in ['text', 'email', 'textarea', 'radio']:
                    val = request.form.get(form_key, '').strip()
                    answers[qid] = val
                elif qtype == 'multiselect':
                    vals = request.form.getlist(form_key)
                    # Handle optional other input
                    other_enabled = q.get('otherOption')
                    other_key = form_key + '__other'
                    other_val = request.form.get(other_key, '').strip() if other_enabled else ''
                    if other_val:
                        vals.append(other_val)
                    answers[qid] = vals
                else:
                    # Fallback to string
                    answers[qid] = request.form.get(form_key, '').strip()

        # Minimal validation: require org.name and org.primaryContact.email if present in questionnaire
        req_org = answers.get('org.name', '')
        req_email = answers.get('org.primaryContact.email', '')
        if not req_org or not req_email or ('@' not in req_email):
            error = 'Please provide your organization name and a valid primary contact email.'
        else:
            # Persist answers to a timestamped JSON file
            ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
            username = session['user']
            ans_dir = os.path.join(os.path.dirname(__file__), 'static', 'data', 'db', 'onboarding_answers')
            os.makedirs(ans_dir, exist_ok=True)
            ans_filename = f"{project_id}_{username}_{ts}.json"
            ans_path = os.path.join(ans_dir, ans_filename)
            payload = {
                'project_id': project_id,
                'username': username,
                'submitted_at': ts,
                'answers': answers
            }
            try:
                with open(ans_path, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
            except Exception as e:
                error = f"Failed to save answers: {e}"

            if not error:
                # Append a record to onboarding_requests.json
                req_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'db', 'onboarding_requests.json')
                record = {
                    'project_id': project_id,
                    'username': username,
                    'submitted_at': ts,
                    'answers_file': os.path.relpath(ans_path, os.path.dirname(__file__)).replace('\\', '/') ,
                    'status': 'submitted'
                }
                try:
                    # Ensure parent directory exists
                    os.makedirs(os.path.dirname(req_path), exist_ok=True)
                    if os.path.exists(req_path):
                        with open(req_path, 'r', encoding='utf-8') as f:
                            existing = json.load(f)
                            if not isinstance(existing, list):
                                existing = []
                    else:
                        existing = []
                    existing.append(record)
                    with open(req_path, 'w', encoding='utf-8') as f:
                        json.dump(existing, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    error = f"Failed to register onboarding request: {e}"

            if not error:
                # Optionally, do not auto-join; keep as pending. Redirect to dashboard with info.
                return redirect(url_for('dashboard'))

    return render_template('onboarding_form.html', project=project, questionnaire=questionnaire, error=error)


@app.route('/project/<project_id>/edit', methods=['POST'])
@login_required
def project_edit(project_id):
    project = next((p for p in projects_catalog if str(p.get('id')) == str(project_id)), None)
    if not project:
        return redirect(url_for('dashboard'))
    username = session['user']
    # Only owner can edit
    if project.get('owner') != username:
        return redirect(url_for('project_manage', project_id=project_id))

    # Minimal editable fields: title; if FDP add study_objective and contact_email
    title = request.form.get('title', '').strip()
    objective = request.form.get('study_objective', '').strip()
    contact_email = request.form.get('contact_email', '').strip()

    if title:
        project['title'] = title
    # Update nested FDP fields if present
    if isinstance(project.get('fdp'), dict):
        if objective:
            project['fdp']['study_objective'] = objective
        if contact_email:
            project['fdp']['contact_email'] = contact_email

    # Optionally update tags from a comma separated list
    tags_raw = request.form.get('tags', '')
    if tags_raw:
        project['tags'] = [t.strip() for t in tags_raw.split(',') if t.strip()]

    save_registry()
    return redirect(url_for('project_manage', project_id=project_id))


@app.route('/project/<project_id>/delete', methods=['POST'])
@login_required
def project_delete(project_id):
    project = next((p for p in projects_catalog if str(p.get('id')) == str(project_id)), None)
    if not project:
        return redirect(url_for('dashboard'))
    username = session['user']
    # Only owner can delete
    if project.get('owner') != username:
        return redirect(url_for('project_manage', project_id=project_id))

    # Remove from catalog
    try:
        projects_catalog.remove(project)
    except ValueError:
        pass

    # Clean participants map
    if project_id in project_participants:
        project_participants.pop(project_id, None)

    # Remove project from all user_projects lists
    for u, plist in list(user_projects.items()):
        if project_id in plist:
            try:
                plist.remove(project_id)
            except ValueError:
                pass

    save_registry()
    return redirect(url_for('dashboard'))


# ---------------- Onboarding Requests Panel ----------------
@app.route('/requests')
@login_required
def onboarding_requests():
    username = session['user']
    all_reqs = load_onboarding_requests()
    # Annotate requests with indices and project title
    annotated = []
    for idx, rec in enumerate(all_reqs):
        proj = next((p for p in projects_catalog if str(p.get('id')) == str(rec.get('project_id'))), None)
        if not proj:
            continue
        if proj.get('owner') != username:
            continue
        annotated.append({
            **rec,
            '_id': idx,
            'project_title': proj.get('title'),
        })
    # Sort: pending first
    annotated.sort(key=lambda r: {'submitted': 0, 'accepted': 1, 'rejected': 1}.get(r.get('status','submitted'), 1))
    return render_template('onboarding_requests.html', requests=annotated)


@app.route('/requests/<int:req_id>')
@login_required
def onboarding_request_detail(req_id):
    all_reqs = load_onboarding_requests()
    if req_id < 0 or req_id >= len(all_reqs):
        abort(404)
    rec = all_reqs[req_id]
    # Authorization: only owner of referenced project
    proj = next((p for p in projects_catalog if str(p.get('id')) == str(rec.get('project_id'))), None)
    if not proj:
        abort(404)
    if proj.get('owner') != session['user']:
        abort(403)

    # Load answers file
    answers = {}
    answers_path = rec.get('answers_file')
    if answers_path:
        try:
            # answers_file is relative to repo root (app dir). Build absolute path
            abs_path = os.path.join(os.path.dirname(__file__), answers_path.replace('/', os.sep))
            with open(abs_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
                answers = payload.get('answers', {})
        except Exception as e:
            answers = {'_error': f'Failed to load answers: {e}'}

    return render_template('onboarding_request_detail.html', req={**rec, '_id': req_id}, project=proj, answers=answers)


@app.route('/requests/<int:req_id>/decide', methods=['POST'])
@login_required
def onboarding_request_decide(req_id):
    all_reqs = load_onboarding_requests()
    if req_id < 0 or req_id >= len(all_reqs):
        abort(404)
    rec = all_reqs[req_id]
    proj = next((p for p in projects_catalog if str(p.get('id')) == str(rec.get('project_id'))), None)
    if not proj:
        abort(404)
    if proj.get('owner') != session['user']:
        abort(403)

    decision = request.form.get('decision', '').strip().lower()  # 'accept' or 'reject'
    reason = request.form.get('reason', '').strip()

    if decision == 'accept':
        rec['status'] = 'accepted'
        rec['rejection_reason'] = ''
        # Add participant to project
        pid = str(proj.get('id'))
        project_participants.setdefault(pid, [])
        if rec.get('username') and rec['username'] not in project_participants[pid]:
            project_participants[pid].append(rec['username'])
        save_registry()
    elif decision == 'reject':
        rec['status'] = 'rejected'
        rec['rejection_reason'] = reason
    else:
        # no-op -> back to detail
        return redirect(url_for('onboarding_request_detail', req_id=req_id))

    rec['decided_at'] = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    rec['decided_by'] = session['user']

    # Persist
    all_reqs[req_id] = rec
    save_onboarding_requests(all_reqs)

    return redirect(url_for('onboarding_request_detail', req_id=req_id))
