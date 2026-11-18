# Django Virtual Labs

A Virtual Labs style landing page built with Django, HTML, CSS and JavaScript.

## Run it

    python -m venv venv
    source venv/bin/activate        # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Open http://127.0.0.1:8000/

## Where things live

- `labs/data.py`: the six labs shown on the home page (edit titles, books, syllabus here)
- `labs/views.py`, `labs/urls.py`: page logic and routes
- `templates/base.html`: header, nav, footer shared by every page
- `templates/labs/home.html`: the lab list and announcements
- `static/css/style.css`, `static/js/main.js`: styling, clock, dropdowns, search
