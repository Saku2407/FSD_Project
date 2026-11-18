"""Run with: python manage.py test"""
from django.test import TestCase
from django.urls import reverse
from .models import LabFeedback, StudentRecord


class VirtualLabTests(TestCase):
    def test_all_sections_render(self):
        for route in ('home', 'aim', 'overview', 'views_page', 'pretest', 'procedure',
                      'simulation', 'template_tags', 'template_filters', 'models_data',
                      'get_post', 'analysis', 'observations', 'posttest', 'references', 'feedback'):
            with self.subTest(route=route):
                response = self.client.get(reverse('views_template:' + route))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Passing Data from Views to Templates')

    def test_simulation_pass_renders_data_and_creates_record(self):
        response = self.client.post(reverse('views_template:simulation'), data={
            'name': 'Test Student', 'course': 'Django Fundamentals',
            'marks': 82, 'skills': 'Python, HTML, Django',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST STUDENT')
        self.assertContains(response, 'PASS')
        self.assertContains(response, 'Python')
        self.assertEqual(StudentRecord.objects.count(), 1)
        self.assertContains(self.client.get(reverse('views_template:models_data')), 'Test Student')
        self.assertContains(self.client.get(reverse('views_template:observations')), 'Test Student')

    def test_simulation_fail_and_validation(self):
        values = {'name': 'Student Two', 'course': 'Web Development', 'marks': 39, 'skills': 'Django'}
        self.assertContains(self.client.post(reverse('views_template:simulation'), values), 'FAIL')
        values['marks'] = 101
        response = self.client.post(reverse('views_template:simulation'), values)
        self.assertContains(response, 'Ensure this value is less than or equal to 100')
        self.assertEqual(StudentRecord.objects.count(), 1)

    def test_autoescape_protects_markup(self):
        response = self.client.post(reverse('views_template:simulation'), data={
            'name': '<script>alert(1)</script>', 'course': 'Python Programming',
            'marks': 90, 'skills': 'Python',
        })
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;')

    def test_quiz_scores(self):
        self.assertContains(self.client.post(reverse('views_template:pretest'), {
            'p1': '1', 'p2': '2', 'p3': '0', 'p4': '2', 'p5': '0',
        }), '5 <small>/ 5</small>', html=False)
        self.assertContains(self.client.get(reverse('views_template:analysis')), '5/5')

    def test_get_and_post_request_display(self):
        url = reverse('views_template:get_post')
        self.assertContains(self.client.get(url + '?message=Hello'), 'Hello')
        self.assertContains(self.client.post(url, {'message': 'Welcome'}), 'Welcome')

    def test_feedback_is_saved_locally(self):
        self.assertContains(self.client.post(reverse('views_template:feedback'), data={
            'kind': 'bug', 'rating': '4', 'message': 'Test feedback message',
        }), 'Thank you!')
        self.assertEqual(LabFeedback.objects.count(), 1)
