
## Create project

```bash
poetry init
poetry add django djangorestframework
poetry add --dev black
poetry add --dev flake8
poetry add --dev isort
poetry add --dev mypy
```

```bash
django-admin startproject djangochat
python manage.py migrate
python manage.py createsuperuser
```

```bash
python manage.py startapp accounts
```

## Run 

```bash
python manage.py runserver 192.168.100.46:8000
```
