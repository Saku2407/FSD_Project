"""Run with python manage.py test; verify the Git practice workflow end-to-end."""
from django.test import TestCase
from django.urls import reverse
from .models import LabFeedback
from .git_simulator import blank_repo, process, head, status


class GitLabTests(TestCase):
    def simulate(self, action, **kwargs):
        return self.client.post(reverse('git_repo_manage:simulation'), {'action': action, **kwargs})

    def test_all_sections_render(self):
        for route in ('home', 'aim', 'overview', 'procedure', 'pretest', 'simulation',
                      'observations', 'analysis', 'posttest', 'references', 'feedback'):
            with self.subTest(route=route):
                r = self.client.get(reverse('git_repo_manage:' + route))
                self.assertEqual(r.status_code, 200)
                self.assertContains(r, 'Git Repository Management')

    def test_complete_workflow_and_fast_forward(self):
        self.assertContains(self.simulate('init'), 'Initialized an empty Git repository')
        for name in ('README.md', 'manage.py', 'requirements.txt'):
            self.assertContains(self.simulate('add', filename=name), 'Staged a snapshot')
        self.assertContains(self.simulate('commit', message='Initial Django project'), 'c0001')
        self.assertContains(self.simulate('branch', branch='feature'), 'Created branch')
        self.assertContains(self.simulate('switch', branch='feature'), 'Switched to branch feature')
        self.assertContains(self.simulate('edit', filename='lab/views.py', content='def index(request): pass'), 'Saved lab/views.py')
        self.assertContains(self.simulate('add', filename='lab/views.py'), 'Staged a snapshot')
        self.assertContains(self.simulate('commit', message='Add home view'), 'c0002')
        self.assertContains(self.simulate('switch', branch='main'), 'Switched to branch main')
        result = self.simulate('merge', branch='feature')
        self.assertContains(result, 'Fast-forward merge completed')
        self.assertContains(result, 'c0002')
        repo = self.client.session['git_repository']
        self.assertEqual(repo['branches']['main'], 'c0002')
        self.assertTrue(status(repo)['clean'])
        self.assertContains(self.client.get(reverse('git_repo_manage:observations')), 'git merge feature')

    def test_cannot_commit_without_staging_and_safe_file_validation(self):
        self.simulate('init')
        self.assertContains(self.simulate('commit', message='Bad commit'), 'Nothing staged')
        self.assertContains(self.simulate('edit', filename='../settings.py', content='bad'), 'Choose an available project file')
        self.assertNotIn('../settings.py', self.client.session['git_repository']['working'])
        self.assertContains(self.simulate('branch', branch='feature'), 'Make the first commit')

    def test_staging_snapshot_and_clean_branch_switch(self):
        repo = blank_repo()
        process(repo, 'init', {})
        process(repo, 'add', {'filename': 'README.md'})
        process(repo, 'edit', {'filename': 'README.md', 'content': 'later edit'})
        self.assertEqual(repo['stage']['README.md'], '# My Django Project\n\nA simple Django application.\n')
        self.assertIn('README.md', status(repo)['modified'])
        process(repo, 'commit', {'message': 'Initial'})
        self.assertEqual(repo['commits'][head(repo)]['files']['README.md'], '# My Django Project\n\nA simple Django application.\n')
        process(repo, 'branch', {'branch': 'feature'})
        self.assertFalse(process(repo, 'switch', {'branch': 'feature'})['success'])

    def test_autoescape_protects_html_in_terminal(self):
        self.simulate('init')
        r = self.simulate('edit', filename='README.md', content='<script>alert(1)</script>')
        self.assertNotContains(r, '<script>alert(1)</script>')
        self.assertContains(r, 'Saved README.md')

    def test_quiz_and_feedback(self):
        q = self.client.post(reverse('git_repo_manage:pretest'), {'p1': '1', 'p2': '0', 'p3': '2', 'p4': '0', 'p5': '3'})
        self.assertContains(q, 'YOUR SCORE')
        self.assertContains(self.client.get(reverse('git_repo_manage:analysis')), '5/5')
        response = self.client.post(reverse('git_repo_manage:feedback'), data={
            'kind': 'bug', 'rating': '4', 'message': 'Check this simulation',
        })
        self.assertContains(response, 'Thank you!')
        self.assertEqual(LabFeedback.objects.count(), 1)
