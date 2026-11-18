"""Educational Django experiment: actual server-side data passing to HTML templates."""
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import ExperimentForm, FeedbackForm
from .models import StudentRecord, LabFeedback
from .questions import POSTTEST, PRETEST

NAVIGATION = [
    {'key': 'aim', 'label': 'Aim'},
    {'key': 'overview', 'label': 'Overview'},
    {'key': 'views_page', 'label': 'Views'},
    {'key': 'pretest', 'label': 'Pretest'},
    {'key': 'simulation', 'label': 'Passing Data from Views to Templates'},
    {'key': 'procedure', 'label': 'Procedure'},
    {'key': 'template_tags', 'label': 'Template Tags'},
    {'key': 'template_filters', 'label': 'Template Filters'},
    {'key': 'models_data', 'label': 'Data from Models to Templates'},
    {'key': 'get_post', 'label': 'GET & POST Data'},
    {'key': 'analysis', 'label': 'Analysis'},
    {'key': 'observations', 'label': 'Observations'},
    {'key': 'posttest', 'label': 'Posttest'},
    {'key': 'references', 'label': 'Further Readings / References'},
    {'key': 'feedback', 'label': 'Feedback'},
]


def base_context(active, page_title):
    return {'active': active, 'page_title': page_title,
            'navigation': [{**item, 'href': reverse('views_template:' + item['key'])} for item in NAVIGATION]}


def home(request):
    return render(request, 'views_template/aim.html', base_context('aim', 'Aim'))


def aim(request):
    return home(request)


def overview(request):
    return render(request, 'views_template/theory.html', base_context('overview', 'Overview'))


def views_page(request):
    return render(request, 'views_template/views_page.html', base_context('views_page', 'Views'))


def procedure(request):
    return render(request, 'views_template/procedure.html', base_context('procedure', 'Procedure'))


def template_tags(request):
    return render(request, 'views_template/template_tags.html', base_context('template_tags', 'Template Tags'))


def template_filters(request):
    return render(request, 'views_template/template_filters.html', base_context('template_filters', 'Template Filters'))


@require_http_methods(['GET', 'POST'])
def simulation(request):
    """Read form data, validate it, prepare a context dict and render it in a template."""
    form = ExperimentForm(request.POST or None, initial={
        'name': 'Yash Kapadiya', 'course': 'Django Fundamentals',
        'marks': 82, 'skills': 'Python, HTML, Django',
    } if request.method == 'GET' else None)
    context = base_context('simulation', 'Passing Data from Views to Templates')
    context.update({'form': form, 'result': None})
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        student = {
            'name': data['name'],
            'course': data['course'],
            'marks': data['marks'],
            'status': 'PASS' if data['marks'] >= 40 else 'FAIL',
            'skills': data['skills'],
        }
        # This is the essential concept: pass the Python dictionary via context.
        context['result'] = student
        context['skill_count'] = len(student['skills'])

        # Session creates observation history for the current browser.
        history = request.session.get('experiment_history', [])
        history.insert(0, {
            'name': student['name'], 'course': student['course'],
            'marks': student['marks'], 'status': student['status'],
            'skill_count': len(student['skills']),
        })
        request.session['experiment_history'] = history[:8]
        if not request.session.session_key:
            request.session.save()
        StudentRecord.objects.create(
            session_key=request.session.session_key,
            name=student['name'], course=student['course'],
            marks=student['marks'], status=student['status'],
            skills=', '.join(student['skills']),
        )
    return render(request, 'views_template/simulation.html', context)


@require_http_methods(['GET', 'POST'])
def observations(request):
    if request.method == 'POST' and request.POST.get('action') == 'clear':
        request.session.pop('experiment_history', None)
        if request.session.session_key:
            StudentRecord.objects.filter(session_key=request.session.session_key).delete()
        return redirect('views_template:observations')
    context = base_context('observations', 'Observations')
    context['history'] = request.session.get('experiment_history', [])
    return render(request, 'views_template/observations.html', context)


def models_data(request):
    context = base_context('models_data', 'Data from Models to Templates')
    context['records'] = (StudentRecord.objects.filter(session_key=request.session.session_key)
                          .order_by('-created_at')[:8] if request.session.session_key else [])
    return render(request, 'views_template/models_data.html', context)


@require_http_methods(['GET', 'POST'])
def get_post(request):
    context = base_context('get_post', 'GET & POST Data')
    if request.method == 'POST':
        message = request.POST.get('message', '')
    else:
        message = request.GET.get('message', '')
    context['message'] = message.strip()[:120]
    context['method_used'] = request.method if context['message'] else None
    return render(request, 'views_template/get_post.html', context)


def analysis(request):
    context = base_context('analysis', 'Analysis')
    context['history'] = request.session.get('experiment_history', [])
    context['pre_score'] = request.session.get('latest_pretest')
    context['post_score'] = request.session.get('latest_posttest')
    return render(request, 'views_template/analysis.html', context)


def _quiz(request, phase, questions, heading):
    context = base_context(phase, heading)
    context['questions'] = [{
        'id': q['id'], 'question': q['question'], 'choices': list(enumerate(q['options']))
    } for q in questions]
    context['result'] = None
    if request.method == 'POST':
        report, score = [], 0
        for q in questions:
            picked = request.POST.get(q['id'], '')
            try:
                selected = int(picked)
            except (TypeError, ValueError):
                selected = -1
            correct = selected == q['answer']
            score += int(correct)
            report.append({
                'question': q['question'], 'correct': correct,
                'chosen': q['options'][selected] if 0 <= selected < len(q['options']) else 'Not answered',
                'answer': q['options'][q['answer']], 'explanation': q['explanation'],
            })
        context['result'] = {'score': score, 'total': len(questions), 'report': report,
                             'percent': round(100 * score / len(questions))}
        request.session[f'latest_{phase}'] = {'score': score, 'total': len(questions)}
    return render(request, 'views_template/quiz.html', context)


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
    return render(request, 'views_template/feedback.html', context)


def references(request):
    return render(request, 'views_template/references.html', base_context('references', 'References'))



def student_view(request):
    data = {
        "name": "Yash Kapadiya",
        "age": 25,
        "course": "Django",
        "marks": 82,
    }

    return render(request, "views_template/student.html", data)
