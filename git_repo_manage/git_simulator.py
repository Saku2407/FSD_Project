"""Deterministic per-session educational Git simulator. No shell commands are executed.

Models snapshots, index/staging, working tree, commits, branches, and fast-forward merges.
This is not a replacement for a real Git repository: it is deliberately constrained.
"""
import copy
import re

FILES = ('README.md', 'manage.py', 'requirements.txt', 'config/settings.py', 'lab/views.py')
STARTER_FILES = {
    'README.md': '# My Django Project\n\nA simple Django application.\n',
    'manage.py': '# Django entry point\nfrom django.core.management import execute_from_command_line\n',
    'requirements.txt': 'Django>=5.2,<6.0\n',
}
BRANCH_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,23}$')


def blank_repo():
    return {'initialized': False, 'current': 'main', 'branches': {}, 'commits': {},
            'next_id': 1, 'working': copy.deepcopy(STARTER_FILES), 'stage': {}, 'events': []}


def head(repo):
    return repo['branches'].get(repo['current']) if repo['initialized'] else None


def snapshot(repo, commit_id):
    if not commit_id:
        return {}
    return repo['commits'][commit_id]['files']


def status(repo):
    if not repo['initialized']:
        return {'staged': [], 'modified': [], 'untracked': list(repo['working']), 'clean': False}
    base = snapshot(repo, head(repo))
    staged = [name for name, value in repo['stage'].items() if base.get(name) != value]
    modified = [name for name, value in repo['working'].items()
                if name in base or name in repo['stage']
                if value != repo['stage'].get(name, base.get(name))]
    untracked = [name for name in repo['working'] if name not in base and name not in repo['stage']]
    return {'staged': sorted(staged), 'modified': sorted(modified),
            'untracked': sorted(untracked), 'clean': not (staged or modified or untracked)}


def _clean(repo):
    return status(repo)['clean']


def _is_ancestor(repo, ancestor, descendant):
    if ancestor is None:
        return True
    while descendant:
        if ancestor == descendant:
            return True
        descendant = repo['commits'][descendant]['parent']
    return False


def perform(repo, action, data):
    """Returns (is_success, human_output, command). Mutates only validated state."""
    if action == 'init':
        command = 'git init'
        if repo['initialized']:
            return False, 'Repository already initialized.', command
        repo['initialized'] = True
        repo['current'] = 'main'
        repo['branches'] = {'main': None}
        return True, 'Initialized an empty Git repository. Next: stage a file with git add.', command
    if action == 'reset':
        repo.clear()
        repo.update(blank_repo())
        return True, 'Practice lab reset. Your simulated repository is now empty.', 'reset lab'
    if not repo['initialized']:
        return False, 'Initialize your repository first using git init.', action

    if action == 'edit':
        filename = data.get('filename', '')
        value = data.get('content', '')
        command = f'edit {filename}'
        if filename not in FILES or len(value) > 1500:
            return False, 'Choose an available project file with at most 1,500 characters.', command
        repo['working'][filename] = value
        return True, f'Saved {filename} in the simulated working directory (not staged yet).', command

    if action == 'add':
        filename = data.get('filename', '')
        command = f'git add {filename}'
        if filename not in repo['working'] or filename not in FILES:
            return False, 'Select a file from the project workspace.', command
        repo['stage'][filename] = repo['working'][filename]
        return True, f'Staged a snapshot of {filename}. Changes made after staging are not automatically staged.', command

    if action == 'commit':
        msg = data.get('message', '').strip()
        command = f'git commit -m "{msg}"'
        if len(msg) < 3 or len(msg) > 100:
            return False, 'Commit message must be 3–100 characters.', command
        base = copy.deepcopy(snapshot(repo, head(repo)))
        changed = {name: value for name, value in repo['stage'].items() if base.get(name) != value}
        if not changed:
            return False, 'Nothing staged to commit. Use git add after editing a file.', command
        base.update(repo['stage'])
        commit_id = f"c{repo['next_id']:04d}"
        repo['next_id'] += 1
        repo['commits'][commit_id] = {'id': commit_id, 'parent': head(repo),
                                      'message': msg, 'files': base, 'branch_created_on': repo['current']}
        repo['branches'][repo['current']] = commit_id
        repo['stage'] = {}
        return True, f'[{repo["current"]} {commit_id}] {msg} ({len(changed)} file(s) changed).', command

    if action == 'branch':
        branch = data.get('branch', '').strip()
        command = f'git branch {branch}'
        if not BRANCH_RE.fullmatch(branch):
            return False, 'Use 1–24 characters: letters, digits, hyphens or underscores; start with a letter.', command
        if branch in repo['branches']:
            return False, 'A branch with that name already exists.', command
        if not head(repo):
            return False, 'Make the first commit before creating a branch.', command
        repo['branches'][branch] = head(repo)
        return True, f'Created branch {branch} at {head(repo)}. Use git switch to change branches.', command

    if action == 'switch':
        branch = data.get('branch', '')
        command = f'git switch {branch}'
        if branch not in repo['branches']:
            return False, 'That branch does not exist yet.', command
        if branch == repo['current']:
            return True, f'Already on branch {branch}.', command
        if not _clean(repo):
            return False, 'Working tree is not clean. Commit your staged/modified files before switching.', command
        repo['current'] = branch
        repo['working'] = copy.deepcopy(snapshot(repo, head(repo)))
        repo['stage'] = {}
        return True, f'Switched to branch {branch}. Workspace now reflects that branch\'s last commit.', command

    if action == 'merge':
        branch = data.get('branch', '')
        command = f'git merge {branch}'
        if branch not in repo['branches']:
            return False, 'Select an existing branch to merge.', command
        if branch == repo['current']:
            return False, 'Choose a different branch to merge.', command
        if not _clean(repo):
            return False, 'Commit your changes before attempting to merge.', command
        current_head, incoming_head = head(repo), repo['branches'][branch]
        if _is_ancestor(repo, incoming_head, current_head):
            return True, 'Already up to date: nothing to merge.', command
        if not _is_ancestor(repo, current_head, incoming_head):
            return False, 'Branches have diverged. This beginner simulator only supports fast-forward merges; use real Git to learn merge commits and conflict resolution.', command
        repo['branches'][repo['current']] = incoming_head
        repo['working'] = copy.deepcopy(snapshot(repo, incoming_head))
        return True, f'Fast-forward merge completed: {repo["current"]} now points to {incoming_head}.', command

    return False, 'Unknown action.', action


def process(repo, action, data):
    success, message, command = perform(repo, action, data)
    event = {'command': command[:155], 'message': message, 'success': success,
             'branch': repo['current'] if repo['initialized'] else '—'}
    # An empty lab after reset should still retain a single reset observation.
    repo['events'] = ([event] + repo['events'])[:30]
    return event


def commit_history(repo):
    sequence = []
    commit_id = head(repo)
    while commit_id and len(sequence) < 25:
        commit = repo['commits'][commit_id]
        sequence.append({'id': commit_id, 'message': commit['message'],
                         'parent': commit['parent'], 'original_branch': commit['branch_created_on']})
        commit_id = commit['parent']
    return sequence
