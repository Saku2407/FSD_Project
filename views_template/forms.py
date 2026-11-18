from django import forms

COURSES = [
    ('Django Fundamentals', 'Django Fundamentals'),
    ('Python Programming', 'Python Programming'),
    ('Web Development', 'Web Development'),
    ('Data Science', 'Data Science'),
]

class ExperimentForm(forms.Form):
    """Values entered in a browser become Python data in the Django view."""
    name = forms.CharField(label='Student name', max_length=60, widget=forms.TextInput(attrs={
        'placeholder': 'e.g. Yash Kapadiya', 'autocomplete': 'off',
    }))
    course = forms.ChoiceField(label='Course', choices=COURSES)
    marks = forms.IntegerField(label='Marks (out of 100)', min_value=0, max_value=100,
                               widget=forms.NumberInput(attrs={'placeholder': 'e.g. 82'}))
    skills = forms.CharField(label='Skills (comma-separated)', max_length=160,
                             help_text='Example: Python, HTML, Django',
                             widget=forms.TextInput(attrs={'placeholder': 'Python, HTML, Django'}))

    def clean_skills(self):
        raw = self.cleaned_data['skills']
        items = [part.strip() for part in raw.split(',') if part.strip()]
        if not items:
            raise forms.ValidationError('Enter at least one skill.')
        if len(items) > 6:
            raise forms.ValidationError('Enter a maximum of six skills.')
        if any(len(item) > 30 for item in items):
            raise forms.ValidationError('Each skill should have 30 characters or fewer.')
        return items


class FeedbackForm(forms.Form):
    kind = forms.ChoiceField(label='Feedback type', choices=[
        ('rating', 'Rating'), ('bug', 'Report a bug'), ('suggestion', 'Suggestion'),
    ])
    rating = forms.IntegerField(label='Rating (1–5, optional)', min_value=1, max_value=5, required=False)
    message = forms.CharField(label='Your feedback', min_length=5, max_length=1000,
                              widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us what worked or what could be improved.'}))
