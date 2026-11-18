"""
Registration form for the Virtual Lab:
Custom Form Validation using clean() in Django

Validation runs in this order when form.is_valid() is called:
  1. Built-in field validation (required, valid email, valid integer ...)
  2. clean_<fieldname>()  ->  one method per field (field-level validation)
  3. clean()              ->  whole-form validation (cross-field checks)
"""

import re

from django import forms
from django.core.exceptions import ValidationError

# Usernames must start with a letter, then contain only letters, digits or "_".
USERNAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

# Names that ordinary users are not allowed to register.
RESERVED_USERNAMES = {
    "admin",
    "administrator",
    "root",
    "superuser",
    "staff",
    "support",
    "moderator",
    "system",
}

# Example of blocked throw-away e-mail domains.
BLOCKED_EMAIL_DOMAINS = {
    "tempmail.com",
    "mailinator.com",
    "10minutemail.com",
    "guerrillamail.com",
}


class RegistrationForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. lab_student01",
                "autocomplete": "username",
            }
        ),
        help_text="4-20 characters. Start with a letter; use only letters, digits and underscore (_).",
        error_messages={
            "required": "Please enter a username.",
        },
    )

    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
        help_text="Use a permanent email address (temporary mail services are not accepted).",
        error_messages={
            "required": "Please enter your email address.",
            "invalid": "That does not look like a valid email address. Example: name@example.com",
        },
    )

    age = forms.IntegerField(
        label="Age",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. 21",
            }
        ),
        help_text="You must be 18 or older to register.",
        error_messages={
            "required": "Please enter your age.",
            "invalid": "Age must be a whole number, for example 21.",
        },
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            }
        ),
        help_text="At least 8 characters, with at least one letter and one digit.",
        error_messages={
            "required": "Please create a password.",
        },
    )

    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Re-enter your password",
                "autocomplete": "new-password",
            }
        ),
        error_messages={
            "required": "Please re-enter your password to confirm it.",
        },
    )

    # ------------------------------------------------------------------
    # Field-level validation: clean_<fieldname>()
    # Rules for these methods:
    #   * read the value from self.cleaned_data["<fieldname>"]
    #   * raise ValidationError if the value is not acceptable
    #   * ALWAYS return the (possibly modified) value
    # ------------------------------------------------------------------
    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if len(username) < 4:
            raise ValidationError(
                "Username is too short. It must have at least 4 characters "
                "(you entered %(count)d).",
                code="username_too_short",
                params={"count": len(username)},
            )

        if len(username) > 20:
            raise ValidationError(
                "Username is too long. Please use 20 characters or fewer "
                "(you entered %(count)d).",
                code="username_too_long",
                params={"count": len(username)},
            )

        if not USERNAME_PATTERN.match(username):
            raise ValidationError(
                "Username must start with a letter and may contain only letters, "
                "digits and underscores (no spaces or special characters).",
                code="username_invalid_chars",
            )

        if username.lower() in RESERVED_USERNAMES:
            raise ValidationError(
                "The username '%(name)s' is reserved. Please choose a different one.",
                code="username_reserved",
                params={"name": username},
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        domain = email.rsplit("@", 1)[-1]

        if domain in BLOCKED_EMAIL_DOMAINS:
            raise ValidationError(
                "Temporary email addresses (%(domain)s) are not allowed. "
                "Please use your regular email address.",
                code="email_blocked_domain",
                params={"domain": domain},
            )

        return email

    def clean_age(self):
        age = self.cleaned_data["age"]

        if age < 18:
            raise ValidationError(
                "You must be at least 18 years old to register. "
                "You entered %(age)d.",
                code="age_too_young",
                params={"age": age},
            )

        if age > 120:
            raise ValidationError(
                "Please enter a realistic age (120 or below).",
                code="age_unrealistic",
            )

        return age

    def clean_password(self):
        password = self.cleaned_data["password"]

        if len(password) < 8:
            raise ValidationError(
                "Password is too short. It must have at least 8 characters.",
                code="password_too_short",
            )

        if not re.search(r"[A-Za-z]", password):
            raise ValidationError(
                "Password must contain at least one letter.",
                code="password_no_letter",
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                "Password must contain at least one digit (0-9).",
                code="password_no_digit",
            )

        return password

    # ------------------------------------------------------------------
    # Form-level validation: clean()
    # Runs AFTER every clean_<fieldname>() method. Use it when a rule
    # depends on more than one field. Fields that already failed are
    # missing from cleaned_data, so always use .get().
    # ------------------------------------------------------------------
    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Cross-field check 1: the two passwords must match.
        # add_error("<field>", ...) attaches the message to that field.
        if password and confirm_password and password != confirm_password:
            self.add_error(
                "confirm_password",
                ValidationError(
                    "The two passwords do not match. Please type the same password in both boxes.",
                    code="password_mismatch",
                ),
            )

        # Cross-field check 2: the password must not contain the username.
        # add_error(None, ...) creates a non-field (form-level) error.
        if username and password and username.lower() in password.lower():
            self.add_error(
                None,
                ValidationError(
                    "For your security, the password must not contain your username.",
                    code="password_contains_username",
                ),
            )

        return cleaned_data