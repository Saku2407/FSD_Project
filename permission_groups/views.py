from django.shortcuts import render, redirect
from django.http import Http404

LAB_TITLE = "Permissions and Groups in Django"
DEPARTMENT = "Computer Science and Engineering"
SIDEBAR = [("lab:introduction", "Introduction"), ("lab:objective", "Objective"), ("lab:experiments", "List of experiments"), ("lab:audience", "Target Audience"), ("lab:alignment", "Course Alignment"), ("lab:feedback", "Feedback")]

EXPERIMENTS = [
 {"slug":"django-auth-system","title":"Understanding the Django Authentication System","desc":"Explore the User, Group and Permission models and understand how Django manages authentication and authorization.","time":"45 minutes"},
 {"slug":"default-permissions","title":"Default Model Permissions","desc":"Understand the add, change, delete and view permissions generated for Django models.","time":"45 minutes"},
 {"slug":"custom-permissions","title":"Creating Custom Permissions","desc":"Define application-specific permissions in a model and assign them to users.","time":"50 minutes"},
 {"slug":"groups-management","title":"Creating and Managing Groups","desc":"Create role-based groups, assign permissions and add users to groups.","time":"60 minutes"},
 {"slug":"permissions-in-views","title":"Checking Permissions in Views","desc":"Protect function-based and class-based views with Django permission checks.","time":"60 minutes"},
 {"slug":"permissions-templates","title":"Permissions in Templates","desc":"Use the perms context variable to control which interface elements a user can see.","time":"40 minutes"},
]

# Each experiment has its own learning content and self-check questions.
DETAILS = {
"django-auth-system": {
"aim":"To understand the components of Django's built-in authentication system and the relationship between users, groups and permissions.",
"overview":"Django provides authentication (identity verification) and authorization (access control) through django.contrib.auth. A User represents an account, a Permission represents an allowed action, and a Group is a collection of permissions that can be assigned to multiple users.",
"video": "https://www.youtube.com/watch?v=tclUzl4UmM8",
"video_embed": "https://www.youtube.com/embed/tclUzl4UmM8",
"recap":["Authentication answers ‘Who are you?’; authorization answers ‘What can you do?’","Users can receive permissions directly or through groups.","Django's built-in models are User, Group and Permission."],
"pretest":[("Which Django app provides the built-in authentication system?",["django.contrib.admin","django.contrib.auth","django.contrib.sessions"],1),("What does a Group mainly contain?",["Templates","Permissions","URL patterns"],1)],
"posttest":[("Which model represents an individual account?",["User","Group","Permission"],0),("Can a user belong to more than one group?",["Yes","No"],0)],
"steps":[("Explore the models","Open the Django admin site and inspect Users, Groups and permissions. These models are provided by django.contrib.auth."),("Understand relationships","A user can have direct permissions and can belong to multiple groups. Groups collect permissions for easier role management.")],
"analysis":"Observe how the same permission can be assigned directly to a user or indirectly through a group. Group-based assignment is easier to maintain when many users share the same role.",
},

"default-permissions": {
"aim":"To identify and use the default permissions Django creates for each model.",
"overview":"When migrations are applied, Django creates model-level permissions: add, change, delete and view. Their codenames usually follow the format app_label.action_modelname, for example library.add_book.",
"recap":["Default permissions are created for each model during migration.","The four standard actions are add, change, delete and view.","Permissions are stored in the auth_permission table."],
"pretest":[("Which is NOT one of the standard model permissions?",["add","change","publish"],2),("When are default permissions created?",["During migrations","When a user logs in","When a template loads"],0)],
"posttest":[("What is the usual codename for changing a Book model in app library?",["library.change_book","change.library.Book","book.change_library"],0),("Which permission allows viewing model records?",["view","add","delete"],0)],
"steps":[("Create a model","Add a simple model such as Book to an installed Django app."),("Run migrations","Run python manage.py makemigrations followed by python manage.py migrate. Django creates the model permissions."),("Inspect permissions","In the admin site, open a user or group and inspect the available permissions.")],
"analysis":"Check the permission codenames and relate them to the application label and model name. Confirm that permissions appear after migrations are applied.",
"video":"https://youtu.be/IF_ZpCiZKkw?si=Iau8dwUB-rslVL9E",
"video_embed": "https://www.youtube.com/embed/Iau8dwUB-rslVL9E"},

"custom-permissions": {
"aim":"To create application-specific permissions and assign them to selected users.",
"overview":"Some applications need actions beyond add, change, delete and view. Django allows custom permissions to be declared in a model's Meta class using the permissions option. After migrations, these permissions can be assigned through the admin site or shell.",
"recap":["Custom permissions are declared in a model's Meta class.","Each permission has a codename and human-readable name.","Use user.has_perm('app_label.codename') to check a permission."],
"pretest":[("Where are custom model permissions declared?",["Meta class","urls.py","settings.py"],0),("Which method checks whether a user has a permission?",["has_perm()","get_url()","is_group()"],0)],
"posttest":[("Which Meta option defines custom permissions?",["permissions","custom_auth","access"],0),("What does has_perm() return?",["A Boolean result","A template","A database table"],0)],
"steps":[("Declare a permission","Inside a model, add class Meta: permissions = [('publish_post', 'Can publish post')]."),("Apply migrations","Run makemigrations and migrate so Django creates the custom permission record."),("Assign and verify","Assign the permission to a user in admin and check it with user.has_perm('app.publish_post').")],
"analysis":"Verify that the custom permission appears after migration and that has_perm() returns True only for users who have been granted that permission.",
"video":"https://youtu.be/IF_ZpCiZKkw?si=MWWl9RXfwOm2z-Et",
"video_embed": "https://www.youtube.com/embed/MWWl9RXfwOm2z-Et"},

"groups-management": {
"aim":"To create groups and use them to manage permissions for users according to their roles.",
"overview":"A Group is a named collection of permissions. For example, an Editors group may be allowed to add and change articles, while a Reviewers group may only view them. Assigning users to groups avoids repeating the same permission setup for every account.",
"recap":["Groups simplify permission management for users with similar responsibilities.","A group can have many permissions and a user can belong to multiple groups.","Users inherit permissions assigned to their groups."],
"pretest":[("What is the main purpose of a Django Group?",["Collect permissions","Store HTML pages","Define database fields"],0),("Can a group be assigned permissions?",["Yes","No"],0)],
"posttest":[("A user added to a group receives its permissions:",["Through group membership","Only after changing password","Never"],0),("Which relation is used to add a user to a group?",["user.groups.add(group)","user.add_group()","Group.user(user)"],0)],
"steps":[("Create a group","In Django admin, open Groups and create a group named Editors."),("Assign permissions","Select permissions such as add article and change article, then save the group."),("Add users","Open a user account, add the Editors group and save. The user now receives the group's permissions.")],
"analysis":"Log in as a user in the group and verify the permitted actions. Remove the user from the group and compare the result to understand inherited access.",
"video":"https://youtu.be/1RDOp_eAsy0?si=CM6yv4dHOUGyfolx",
"video_embed": "https://www.youtube.com/embed/CM6yv4dHOUGyfolx"},

"permissions-in-views": {
"aim":"To restrict access to Django views based on the permissions assigned to the current user.",
"overview":"Authorization should be enforced on the server side. Django provides user.has_perm(), the @permission_required decorator for function-based views and PermissionRequiredMixin for class-based views.",
"recap":["Always enforce access control in the view, not only in the interface.","has_perm() checks a permission for the current user.","Decorators and mixins provide reusable access restrictions."],
"pretest":[("Which decorator protects a function-based view?",["@permission_required","@login_url","@group_required"],0),("What is used with class-based views?",["PermissionRequiredMixin","TemplateMixin","URLPermission"],0)],
"posttest":[("What does permission_required do when permission is missing by default?",["Redirects to login","Grants access","Deletes the user"],0),("Which method can manually check access?",["request.user.has_perm()","request.has_perm()","user.permission()"],0)],
"steps":[("Function-based view","Add @permission_required('app.view_report', raise_exception=True) above a view that should be restricted."),("Class-based view","Inherit PermissionRequiredMixin and set permission_required = 'app.view_report'."),("Manual check","Inside a view, use request.user.has_perm('app.view_report') before returning protected data.")],
"analysis":"Test the view with an authorized user, an authenticated user without permission and an anonymous visitor. Confirm that access is granted only to the intended user.",
"video":"https://youtu.be/Naxf3eMOmBU?si=tWLmpxeAVQR2mh7O",
"video_embed": "https://www.youtube.com/embed/tWLmpxeAVQR2mh7O"},

"permissions-templates": {
"aim":"To conditionally display template elements based on the permissions of the logged-in user.",
"overview":"Django makes the perms variable available in templates when the authentication context processor is enabled. It can be used to show or hide links and controls, for example {% if perms.blog.add_post %}. This improves the user experience, but it does not replace permission checks in views.",
"recap":["The perms variable exposes the current user's permissions in templates.","Use perms.app_label.permission_codename in conditions.","Hiding a button is not a substitute for server-side authorization."],
"pretest":[("Which variable exposes permissions in Django templates?",["perms","groups_list","auth"],0),("Does hiding a link secure the underlying view?",["No","Yes"],0)],
"posttest":[("Which condition checks add_post for the blog app?",["perms.blog.add_post","user.blog.add_post","request.add_post"],0),("Where must access still be checked?",["In the view","Only in CSS","Only in the menu"],0)],
"steps":[("Check context processor","Ensure django.contrib.auth.context_processors.auth is listed in the template context processors."),("Add a template condition","Use {% if perms.blog.add_post %} ... {% endif %} around the relevant action link."),("Verify access","Sign in with users having different permissions and compare the visible controls. Also protect the destination view.")],
"analysis":"Compare the template display for users with and without the permission. Then try accessing the URL directly to confirm that the view independently enforces authorization.",
"video":"https://youtu.be/pqxdLl527s0?si=0g9aVeJdJi8OoK54",
"video_embed": "https://www.youtube.com/embed/0g9aVeJdJi8OoK54"}
}

SECTION_LINKS = [("aim","Aim"),("overview","Overview"),("recap","Recap"),("pretest","Pretest"),("steps","Experiment"),("code","Code Assessment"),("analysis","Analysis"),("posttest","Posttest"),("references","Further Readings/References"),("feedback","Feedback")]

def _ctx(request, active, **extra):
    ctx = {"lab_title": LAB_TITLE, "department": DEPARTMENT, "sidebar": SIDEBAR, "active": active}
    ctx.update(extra)
    return ctx

def introduction(request): return render(request, "lab/introduction.html", _ctx(request, "lab:introduction"))
def objective(request): return render(request, "lab/objective.html", _ctx(request, "lab:objective"))
def experiments(request): return render(request, "lab/experiments.html", _ctx(request, "lab:experiments", experiments=EXPERIMENTS))
def experiment_detail(request, slug):
    """Open an experiment at its first section instead of showing all sections together."""
    experiment = next((item for item in EXPERIMENTS if item["slug"] == slug), None)
    if experiment is None:
        raise Http404("Experiment not found")
    return redirect("lab:experiment_section", slug=slug, section="aim")


def experiment_section(request, slug, section):
    """Render exactly one learning section for the selected experiment."""
    experiment = next((item for item in EXPERIMENTS if item["slug"] == slug), None)
    if experiment is None or slug not in DETAILS:
        raise Http404("Experiment not found")
    valid_sections = {key for key, _label in SECTION_LINKS}
    if section not in valid_sections:
        raise Http404("Experiment section not found")

    detail = DETAILS[slug]
    quiz_feedback = None
    if request.method == "POST" and section in ("pretest", "posttest"):
        questions = detail[section]
        score = sum(
            1 for i, question in enumerate(questions)
            if request.POST.get(f"{section}_{i}", "") == str(question[2])
        )
        quiz_feedback = {"score": score, "total": len(questions)}

    section_index = next(i for i, (key, _label) in enumerate(SECTION_LINKS) if key == section)
    previous_section = SECTION_LINKS[section_index - 1] if section_index > 0 else None
    next_section = SECTION_LINKS[section_index + 1] if section_index < len(SECTION_LINKS) - 1 else None
    return render(request, "lab/experiment_detail.html", _ctx(
        request, "", experiment=experiment, detail=detail,
        section_links=SECTION_LINKS, current_section=section,
        quiz_feedback=quiz_feedback, previous_section=previous_section,
        next_section=next_section,
    ))
def audience(request): return render(request, "lab/audience.html", _ctx(request, "lab:audience"))
def alignment(request): return render(request, "lab/alignment.html", _ctx(request, "lab:alignment"))
def feedback(request): return render(request, "lab/feedback.html", _ctx(request, "lab:feedback", submitted=request.method == "POST"))
def home(request): return render(request, "lab/simple.html", _ctx(request, "", page_title="Home", body="Welcome to the Django Permissions and Groups virtual lab. Use the menu on the left to begin."))
def partners(request): return render(request, "lab/simple.html", _ctx(request, "", page_title="Partners", body="This lab is part of a Virtual Labs style initiative supported by partner institutions."))
def contact(request): return render(request, "lab/simple.html", _ctx(request, "", page_title="Contact", body="Phone: General Information: 011-26582050 | Email: support@vlabs.ac.in"))
