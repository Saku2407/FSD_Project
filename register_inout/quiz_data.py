QUIZZES = {

    "registration": {

        "pretest": {

            "beginner": [

                {"id": 1, "q": "Which Django object is commonly used to represent an application's user account?", "options": ["User model", "HttpResponse", "URLconf", "Template"], "answer": "User model", "explanation": "Django provides a built-in User model for authentication."},

                {"id": 2, "q": "Which form is designed to help create a Django user safely?", "options": ["UserCreationForm", "ModelFormSet", "AdminForm", "FileForm"], "answer": "UserCreationForm", "explanation": "UserCreationForm includes password fields and password validation."},

                {"id": 3, "q": "Why should a password not be stored as plain text?", "options": ["It exposes credentials", "It makes CSS slower", "It breaks URLs", "It disables templates"], "answer": "It exposes credentials", "explanation": "Plain-text passwords create a serious security risk. Django stores password hashes."},

            ],

            "advanced": [

                {"id": 4, "q": "What does form.is_valid() do?", "options": ["Runs validation and populates cleaned_data", "Starts the server", "Creates a migration", "Logs out the user"], "answer": "Runs validation and populates cleaned_data", "explanation": "A valid form has passed field and form-level validation."},

                {"id": 5, "q": "Why is commit=False sometimes used when saving a ModelForm?", "options": ["To modify the object before saving", "To disable validation", "To skip CSRF", "To delete the object"], "answer": "To modify the object before saving", "explanation": "commit=False returns an unsaved model instance that can be adjusted first."},

                {"id": 6, "q": "Which token protects a normal Django POST form against CSRF?", "options": ["csrf_token", "auth_token", "session_key", "user_token"], "answer": "csrf_token", "explanation": "The csrf_token template tag supplies the CSRF token used by Django's protection."},

            ],

        },

        "posttest": {

            "beginner": [

                {"id": 7, "q": "What happens when UserCreationForm is valid and save() is called?", "options": ["A user is created", "The server stops", "The database is deleted", "The user is logged out"], "answer": "A user is created", "explanation": "The form creates a User instance with a properly handled password."},

                {"id": 8, "q": "Where are Django users stored by default with SQLite?", "options": ["The database", "The CSS file", "The URL file", "The browser title"], "answer": "The database", "explanation": "Django's auth app stores users in database tables."},

                {"id": 9, "q": "Which HTTP method should a registration form normally use?", "options": ["POST", "GET", "HEAD", "TRACE"], "answer": "POST", "explanation": "Registration changes server-side data, so POST is appropriate."},

            ],

            "advanced": [

                {"id": 10, "q": "What is the main purpose of password hashing?", "options": ["Avoid storing the original password", "Make pages colorful", "Create URLs", "Run JavaScript"], "answer": "Avoid storing the original password", "explanation": "A password hash allows Django to verify a password without storing the original value."},

                {"id": 11, "q": "Which object contains submitted POST form data?", "options": ["request.POST", "request.GET", "request.FILES only", "request.user only"], "answer": "request.POST", "explanation": "request.POST contains form-encoded POST data."},

                {"id": 12, "q": "Why does a registration form include password1 and password2?", "options": ["To confirm the password", "To create two users", "To disable hashing", "To create two sessions"], "answer": "To confirm the password", "explanation": "The two entries help detect accidental password typing errors."},

            ],

        },

    },

    "login": {

        "pretest": {

            "beginner": [

                {"id": 13, "q": "Which function checks credentials?", "options": ["authenticate()", "render()", "redirect()", "logout()"], "answer": "authenticate()", "explanation": "authenticate() checks the supplied credentials using Django's authentication backends."},

                {"id": 14, "q": "Which function logs an authenticated user into a session?", "options": ["login()", "save()", "render()", "migrate()"], "answer": "login()", "explanation": "login() attaches the authenticated user to the current session."},

                {"id": 15, "q": "What does request.user provide?", "options": ["The current user object", "The current URL", "The CSS file", "The database schema"], "answer": "The current user object", "explanation": "Authentication middleware makes request.user available to views."},

            ],

            "advanced": [

                {"id": 16, "q": "What should happen if authentication fails?", "options": ["Do not call login()", "Always create a user", "Delete the database", "Call migrate()"], "answer": "Do not call login()", "explanation": "login() should only be called after successful authentication."},

                {"id": 17, "q": "What allows authentication state to persist across requests?", "options": ["Session", "Template", "CSS", "Migration"], "answer": "Session", "explanation": "Django uses session state to associate the browser with an authenticated user."},

                {"id": 18, "q": "Which class is useful for a standard Django username/password login form?", "options": ["AuthenticationForm", "UserCreationForm only", "FileField", "ModelAdmin"], "answer": "AuthenticationForm", "explanation": "AuthenticationForm provides the standard credential validation behavior."},

            ],

        },

        "posttest": {

            "beginner": [

                {"id": 19, "q": "What is the usual sequence for login?", "options": ["Validate credentials, then login", "Logout, then login", "Migrate, then login", "Render, then delete user"], "answer": "Validate credentials, then login", "explanation": "The user must be authenticated before login() creates the authenticated session."},

                {"id": 20, "q": "What can a logged-in view display using request.user?", "options": ["Username", "CSS source only", "Migration file", "URL pattern"], "answer": "Username", "explanation": "request.user exposes the current authenticated user."},

                {"id": 21, "q": "What does incorrect login input normally cause?", "options": ["A validation error", "Automatic registration", "Database deletion", "Server shutdown"], "answer": "A validation error", "explanation": "The login form reports that the credentials are invalid."},

            ],

            "advanced": [

                {"id": 22, "q": "Why should authenticate() be used instead of manually comparing stored passwords?", "options": ["Django handles authentication and password checking", "It creates CSS", "It avoids all forms", "It disables sessions"], "answer": "Django handles authentication and password checking", "explanation": "Django's authentication system uses the configured backends and password hashing."},

                {"id": 23, "q": "What does login(request, user) need?", "options": ["A valid User object", "A template name only", "A migration file", "A CSS selector"], "answer": "A valid User object", "explanation": "The authenticated user is associated with the request's session."},

                {"id": 24, "q": "What is the role of AuthenticationMiddleware?", "options": ["It makes request.user available", "It creates CSS", "It writes migrations", "It compiles templates"], "answer": "It makes request.user available", "explanation": "AuthenticationMiddleware associates the user with each request when session middleware is enabled."},

            ],

        },

    },

    "logout": {

        "pretest": {

            "beginner": [

                {"id": 25, "q": "Which function signs a user out?", "options": ["logout()", "login()", "authenticate()", "render()"], "answer": "logout()", "explanation": "logout() clears the authenticated state from the session."},

                {"id": 26, "q": "What does @login_required do?", "options": ["Restricts a view to logged-in users", "Creates users", "Runs migrations", "Adds CSS"], "answer": "Restricts a view to logged-in users", "explanation": "Unauthenticated users are redirected to the configured login URL."},

                {"id": 27, "q": "After logout, should a protected dashboard remain accessible?", "options": ["No", "Yes, always", "Only after migration", "Only with CSS"], "answer": "No", "explanation": "A protected view should reject anonymous users."},

            ],

            "advanced": [

                {"id": 28, "q": "Why is POST useful for a logout button?", "options": ["Logout changes server-side state", "GET is always invalid", "POST creates CSS", "POST creates migrations"], "answer": "Logout changes server-side state", "explanation": "State-changing actions are better represented by POST requests."},

                {"id": 29, "q": "What does an anonymous request.user represent?", "options": ["A user who is not authenticated", "A superuser", "A staff user", "A database administrator"], "answer": "A user who is not authenticated", "explanation": "Django uses AnonymousUser for unauthenticated requests."},

                {"id": 30, "q": "What is authorization?", "options": ["Deciding what an authenticated user may access", "Checking password syntax only", "Creating migrations", "Rendering HTML"], "answer": "Deciding what an authenticated user may access", "explanation": "Authentication identifies the user; authorization controls access."},

            ],

        },

        "posttest": {

            "beginner": [

                {"id": 31, "q": "What should happen after logout?", "options": ["The user becomes unauthenticated", "A new user is created", "The password changes", "The database is deleted"], "answer": "The user becomes unauthenticated", "explanation": "logout() removes the authenticated session state."},

                {"id": 32, "q": "Which decorator protects a view?", "options": ["@login_required", "@csrf_exempt", "@staticmethod", "@property"], "answer": "@login_required", "explanation": "It restricts access to authenticated users."},

                {"id": 33, "q": "What should a logged-out user normally see when opening a protected dashboard?", "options": ["Login page", "Admin database", "Password hash", "Migration output"], "answer": "Login page", "explanation": "The login_required decorator redirects anonymous users to the login URL."},

            ],

            "advanced": [

                {"id": 34, "q": "What is the relationship between authentication and authorization?", "options": ["Authentication identifies; authorization controls access", "They are identical", "Authorization creates passwords", "Authentication creates CSS"], "answer": "Authentication identifies; authorization controls access", "explanation": "The two concepts solve different security problems."},

                {"id": 35, "q": "Why should a protected view use login_required even if the page has a hidden link?", "options": ["UI hiding is not access control", "Hidden links are secure", "It is only for CSS", "It creates migrations"], "answer": "UI hiding is not access control", "explanation": "A user can type a URL directly, so the server must enforce access."},

                {"id": 36, "q": "What should be verified after logout during testing?", "options": ["Protected pages no longer allow anonymous access", "CSS is deleted", "The User model is removed", "All users are deleted"], "answer": "Protected pages no longer allow anonymous access", "explanation": "The key behavior is that the authentication state has ended."},

            ],

        },

    },

}