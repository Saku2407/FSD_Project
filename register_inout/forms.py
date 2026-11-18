from django import forms

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.contrib.auth.models import User

 

from .models import CodeSubmission, Feedback

 

 

class RegistrationForm(UserCreationForm):

    full_name = forms.CharField(max_length=150, label="Full Name")

    email = forms.EmailField(label="Email")

 

    class Meta:

        model = User

        fields = ("username", "full_name", "email", "password1", "password2")

 

 

class LoginForm(AuthenticationForm):

    username = forms.CharField(label="Username")

    password = forms.CharField(

        label="Password",

        widget=forms.PasswordInput

    )

 

 

class FeedbackForm(forms.ModelForm):

    class Meta:

        model = Feedback

        fields = ("name", "rating", "comments", "suggestions")

        widgets = {

            "comments": forms.Textarea(attrs={"rows": 5}),

            "suggestions": forms.Textarea(attrs={"rows": 4}),

        }

 

 

class CodeSubmissionForm(forms.ModelForm):

    class Meta:

        model = CodeSubmission

        fields = ("student_name", "code")

        widgets = {

            "code": forms.Textarea(

                attrs={

                    "rows": 16,

                    "placeholder": "Write your solution here..."

                }

            )

        }