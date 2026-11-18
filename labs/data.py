"""Lab catalogue. Edit this list to change what the home page shows.

Later, you can replace it with a Lab model (see the "Creating Django Models
and Migrations" lab) and query it with Lab.objects.all().
"""

INSTITUTE = "Somaiya MUMBAI"

LABS = [
    {
        "slug": "git-repository-management",
        "title": "Git Repository Management for a Django Project",
        "institute": INSTITUTE,
        "summary": "Initialise a repository, write a .gitignore for Django, branch, commit, merge and push to a remote.",
        "books": [
            "Pro Git - Scott Chacon and Ben Straub",
            "Django for Beginners - William S. Vincent",
        ],
        "syllabus": [
            "Version control basics",
            "Branching and merging",
            "Remote repositories",
        ],
    },
    {
        "slug": "models-and-migrations",
        "title": "Creating Django Models and Migrations",
        "institute": INSTITUTE,
        "summary": "Define models, generate migrations with makemigrations, apply them with migrate and inspect the schema.",
        "books": [
            "Django for Beginners - William S. Vincent",
            "Two Scoops of Django - Daniel and Audrey Feldroy",
        ],
        "syllabus": [
            "Model fields and options",
            "Migration workflow",
            "Django ORM queries",
        ],
        "launch_url": "/models/",
    },
    {
        "slug": "registration-login-logout",
        "title": "User Registration, Login and Logout",
        "institute": INSTITUTE,
        "summary": "Build sign-up, login and logout flows using django.contrib.auth and UserCreationForm.",
        "books": [
            "Django for Beginners - William S. Vincent",
            "Django official documentation: Authentication",
        ],
        "syllabus": [
            "Authentication system",
            "Sessions and cookies",
            "Login-required views",
        ],
    },
    {
        "slug": "permissions-and-groups",
        "title": "Permissions and Groups in Django",
        "institute": INSTITUTE,
        "summary": "Assign model permissions, organise users into groups and restrict views with permission checks.",
        "books": [
            "Two Scoops of Django - Daniel and Audrey Feldroy",
            "Django official documentation: Authorization",
        ],
        "syllabus": [
            "Default model permissions",
            "Groups and role design",
            "permission_required and has_perm",
        ],
        "launch_url": "/permissions/",
    },
    {
        "slug": "views-to-templates",
        "title": "Passing Data from Views to Templates",
        "institute": INSTITUTE,
        "summary": "Send context dictionaries from views to templates and render them with template tags and filters.",
        "books": [
            "Django for Beginners - William S. Vincent",
            "Django official documentation: Templates",
        ],
        "syllabus": [
            "Context dictionaries",
            "Template tags and filters",
            "Template inheritance",
        ],
        "launch_url": "/data/",
    },
    {
        "slug": "custom-form-validation-clean",
        "title": "Custom Form Validation using clean()",
        "institute": INSTITUTE,
        "summary": "Validate fields together by overriding clean() and raising ValidationError with clear messages.",
        "books": [
            "Django official documentation: Form and field validation",
            "Two Scoops of Django - Daniel and Audrey Feldroy",
        ],
        "syllabus": [
            "Form and field validation",
            "clean_<field>() and clean()",
            "Displaying form errors",
        ],
    },
]
