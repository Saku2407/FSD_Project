"""Git Repository Management virtual lab: session-only simulation and quizzes."""
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import FeedbackForm
from .git_simulator import FILES, blank_repo, commit_history, head, process, status
from .models import LabFeedback
from .questions import PRETEST, POSTTEST

NAVIGATION = [
    {'key': 'aim', 'label': 'Aim'},
    {'key': 'overview', 'label': 'Theory / Overview'},
    {'key': 'procedure', 'label': 'Procedure'},
    {'key': 'pretest', 'label': 'Pretest'},
    {'key': 'simulation', 'label': 'Git Repository Management — Simulation'},
    {'key': 'observations', 'label': 'Observations'},
    {'key': 'analysis', 'label': 'Result & Analysis'},
    {'key': 'posttest', 'label': 'Posttest'},
    {'key': 'references', 'label': 'Further Readings / References'},
    {'key': 'feedback', 'label': 'Feedback'},
]


def base_context(active, page_title):
    return {'active': active, 'page_title': page_title,
            'navigation': [{**item, 'href': reverse('git_repo_manage:' + item['key'])} for item in NAVIGATION]}


def home(request):
    return aim(request)


def aim(request):
    return render(request, 'git_repo_manage/aim.html', base_context('aim', 'Aim'))


def overview(request):
    return render(request, 'git_repo_manage/theory.html', base_context('overview', 'Theory'))


def procedure(request):
    return render(request, 'git_repo_manage/procedure.html', base_context('procedure', 'Procedure'))


@require_http_methods(['GET', 'POST'])
def simulation(request):
    repo = request.session.get('git_repository')
    if repo is None:
        repo = blank_repo()
    event = None
    if request.method == 'POST':
        event = process(repo, request.POST.get('action', ''), request.POST)
        request.session['git_repository'] = repo
        request.session.modified = True
    context = base_context('simulation', 'Interactive Git Simulation')
    context.update({'repo': repo, 'head_id': head(repo), 'state': status(repo),
                    'history': commit_history(repo), 'files': FILES, 'event': event,
                    'events': repo['events'][:8],
                    'workspace': [{'name': name, 'content': repo['working'].get(name, ''),
                                   'exists': name in repo['working']} for name in FILES]})
    return render(request, 'git_repo_manage/simulation.html', context)


@require_http_methods(['GET', 'POST'])
def observations(request):
    repo = request.session.get('git_repository') or blank_repo()
    if request.method == 'POST' and request.POST.get('action') == 'clear_history':
        repo['events'] = []
        request.session['git_repository'] = repo
        return redirect('git_repo_manage:observations')
    context = base_context('observations', 'Observations')
    context.update({'events': repo['events'], 'repo': repo, 'state': status(repo)})
    return render(request, 'git_repo_manage/observations.html', context)


def analysis(request):
    repo = request.session.get('git_repository') or blank_repo()
    context = base_context('analysis', 'Result & Analysis')
    context.update({'repo': repo, 'state': status(repo), 'history': commit_history(repo),
                    'pre_score': request.session.get('latest_pretest'),
                    'post_score': request.session.get('latest_posttest')})
    return render(request, 'git_repo_manage/analysis.html', context)


def _quiz(request, phase, questions, heading):
    context = base_context(phase, heading)
    context['questions'] = [{'id': q['id'], 'question': q['question'],
                             'choices': list(enumerate(q['options']))} for q in questions]
    context['result'] = None
    if request.method == 'POST':
        report, score = [], 0
        for q in questions:
            try:
                selected = int(request.POST.get(q['id'], ''))
            except (ValueError, TypeError):
                selected = -1
            correct = selected == q['answer']
            score += int(correct)
            report.append({'question': q['question'], 'correct': correct,
                           'chosen': q['options'][selected] if 0 <= selected < len(q['options']) else 'Not answered',
                           'answer': q['options'][q['answer']], 'explanation': q['explanation']})
        context['result'] = {'score': score, 'total': len(questions), 'report': report,
                             'percent': round(100 * score / len(questions))}
        request.session[f'latest_{phase}'] = {'score': score, 'total': len(questions)}
    return render(request, 'git_repo_manage/quiz.html', context)


@require_http_methods(['GET', 'POST'])
def pretest(request):
    return _quiz(request, 'pretest', PRETEST, 'Pretest')


@require_http_methods(['GET', 'POST'])
def posttest(request):
    return _quiz(request, 'posttest', POSTTEST, 'Posttest')


@require_http_methods(['GET', 'POST'])
def feedback(request):
    context = base_context('feedback', 'Feedback')
    initial_type = request.GET.get('type') if request.GET.get('type') in ('rating', 'bug', 'suggestion') else 'rating'
    form = FeedbackForm(request.POST or None, initial={'kind': initial_type})
    context.update({'form': form, 'submitted': False})
    if request.method == 'POST' and form.is_valid():
        LabFeedback.objects.create(**form.cleaned_data)
        context['submitted'] = True
        context['form'] = FeedbackForm(initial={'kind': initial_type})
    return render(request, 'git_repo_manage/feedback.html', context)


def references(request):
    return render(request, 'git_repo_manage/references.html', base_context('references', 'References'))
