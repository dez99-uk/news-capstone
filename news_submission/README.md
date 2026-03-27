# Capstone Project Submission - News Application

This submission contains a complete Django News Application built from scratch for the capstone brief. It includes:

- a custom user model with role-based groups and permissions
- publishers, articles, newsletters, and reader subscriptions
- editor review and approval workflow
- email + internal API logging when an article is approved
- REST API with token authentication
- automated Python unit tests
- MariaDB as the default database configuration, with an optional SQLite fallback
- planning, research, and diagram documents

## Submission structure

```text
news_submission/
├── README.md
├── manage.py
├── requirements.txt
├── .env.example
├── Planning/
├── Research/
├── Diagrams/
├── news_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── news_app/
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── permissions.py
    └── tests.py
```

## Functional requirements covered

- Subscribers can view approved articles.
- Journalists can create, update, and delete their own articles.
- Editors can review, approve, update, and delete articles.
- Subscribers can subscribe to publishers using newsletter subscriptions.
- `GET /api/articles/` returns approved articles.
- `GET /api/articles/subscribed/` returns only subscribed approved content for the authenticated subscriber.
- `GET /api/articles/<id>/` returns a single article.
- `POST /api/articles/` allows journalists to create.
- `PUT /api/articles/<id>/` allows journalists to update their own work and editors to update any article.
- `DELETE /api/articles/<id>/` allows journalists to delete their own work and editors to delete any article.
- `POST /api/articles/<id>/approve/` allows editors to approve.
- `POST /api/approved/` records the internal approval log with an internal API key.
- Articles send subscriber emails and trigger an internal POST when approved.

## Tech stack

- Python
- Django
- Django REST Framework
- DRF Token Authentication
- Requests
- PyMySQL for MariaDB connectivity

## Setup instructions

### 1. Clone the repository and enter the project folder

```bash
git clone <your-github-repo-url>
cd <your-repository-folder>
```

After cloning, you should be inside the project root where `manage.py`, `requirements.txt`, and `.env.example` are all located.

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file from `.env.example`

Windows:

```bash
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

### 5. MariaDB is the default database

The provided `.env.example` is already configured for MariaDB:

```env
DB_ENGINE=mariadb
DB_NAME=news_capstone_db
DB_USER=news_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=3306
```

Update `DB_USER` and `DB_PASSWORD` in your `.env` file to match the MariaDB user you create on your machine.

### 6. Create the MariaDB database and user

Open the MariaDB or MySQL client:

```bash
mysql -u root -p
```

Then run:

```sql
CREATE DATABASE news_capstone_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON news_capstone_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

If you choose a different username or password, make the same changes in your `.env` file:

```env
DB_USER=news_user
DB_PASSWORD=strong_password_here
```

### 7. Apply migrations

```bash
python manage.py migrate
```

### 8. Create a superuser

```bash
python manage.py createsuperuser
```

### 9. Run the development server

```bash
python manage.py runserver
```

### 10. Optional SQLite fallback

If you want to run the project with SQLite instead, update `.env` to:

```env
DB_ENGINE=sqlite
DB_NAME=db.sqlite3
```

Then run migrations again.

## API authentication

Create a token for a user from Django shell or admin. Example shell approach:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

user = get_user_model().objects.get(username='your_username')
token, _ = Token.objects.get_or_create(user=user)
print(token.key)
```

Use the token in requests:

```text
Authorization: Token <token>
```

## Running tests

To run the test suite:

```bash
python manage.py test
```

## Notes

- The diagrams folder is included for use case, sequence, CRUD, and ERD files.
- The internal API logging endpoint is intentionally local for assessment/demo purposes.
- For testing, email and external integration calls are mocked where appropriate.
