from django import forms


class FeedbackForm(forms.Form):
    kind = forms.ChoiceField(label='Feedback type', choices=[
        ('rating', 'Rating'), ('bug', 'Report a bug'), ('suggestion', 'Suggestion'),
    ])
    rating = forms.IntegerField(label='Rating (1–5, optional)', min_value=1, max_value=5, required=False)
    message = forms.CharField(label='Your feedback', min_length=5, max_length=1000,
                              widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us what worked or what could be improved.'}))
