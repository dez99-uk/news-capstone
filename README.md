# News Capstone Project - Role-Based News Application

## Project overview

This repository contains a Django-based news application created for the capstone consolidation task.  
The project demonstrates application development, role-based access control, Sphinx documentation,
Git branching, and Docker containerisation in a single portfolio-ready submission.

The application solves a simple newsroom workflow problem:

- **journalists** need a place to create articles and newsletters,
- **editors** need to review and approve content before it becomes public,
- **readers** need access to approved content and subscription-based updates.

The project combines a traditional Django web interface with a small REST API so that the same
domain model can be used from both HTML pages and API endpoints.

## Purpose and scope

The purpose of the application is to model a lightweight publishing workflow with:

- custom user roles,
- approval and moderation of articles,
- newsletter management,
- subscriber notifications,
- token-protected API access,
- generated documentation using Sphinx,
- container-based execution using Docker.

This project is intended for assessment and portfolio demonstration purposes rather than production use.

## Key features

- Custom `User` model with **reader**, **editor**, and **journalist** roles
- Publisher, article, newsletter, and approval log models
- Editor-only article approval workflow
- Subscriber notifications when an article is approved
- Internal API logging for approved articles
- REST API endpoints for articles, newsletters, publishers, users, and token bootstrap
- Django admin configuration for content management
- Unit and API tests
- Sphinx-generated project documentation
- Docker support for running the application in a container

## Repository structure

```text
.
├── Diagrams/
├── Planning/
├── Research/
├── docs/
│   └── source/
├── news_app/
├── news_project/
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── capstone.txt
├── manage.py
└── requirements.txt
```

## Main dependencies

The project relies on the packages listed in `requirements.txt`. Key dependencies include:

- Django
- Django REST Framework
- DRF Token Authentication
- requests
- python-dotenv
- PyMySQL or mysqlclient, depending on how MariaDB/MySQL is configured

Install all project dependencies with:

```bash
pip install -r requirements.txt
```

## Environment variables and configuration

A sample environment file is provided as `.env.example`.  
Create a local `.env` file before running the application.

Typical configuration values include:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=mariadb
DB_NAME=news_capstone_db
DB_USER=news_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@newsapp.local
INTERNAL_API_BASE_URL=http://127.0.0.1:8000
INTERNAL_API_KEY=change-me-internal-key
```

Do **not** commit real credentials, passwords, or API keys to a public repository.

## Manual installation with a virtual environment

### 1. Clone the repository

```bash
git clone https://github.com/dez99-uk/news-capstone.git
cd news-capstone
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

Windows:

```bash
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

### 5. Configure the database

The default setup uses **MariaDB/MySQL**.

Open your database client:

```bash
mysql -u root -p
```

Create the database and user:

```sql
CREATE DATABASE news_capstone_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON news_capstone_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Update `.env` so that `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST`, and `DB_PORT` match your local setup.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. Run the application

```bash
python manage.py runserver
```

### 9. Open the site

```text
http://127.0.0.1:8000
```

## Docker setup

The project can also be started using Docker.

### 1. Build the image

```bash
docker build -t news-capstone .
```

### 2. Run the container

```bash
docker run -p 8000:8000 news-capstone
```

### 3. Open the site

```text
http://127.0.0.1:8000
```

## Usage guide

### Web interface

After signing in, the behaviour depends on the user's role:

- **Readers** can browse approved articles and newsletters.
- **Journalists** can create and manage their own content.
- **Editors** can review and approve pending articles.

### API usage

The project includes token-authenticated API endpoints.

Example: obtain a token with the bootstrap endpoint.

**Input**

```json
{
  "username": "editor",
  "password": "pass12345"
}
```

**Output**

```json
{
  "token": "generated-token-value"
}
```

The returned token can then be used in requests with:

```text
Authorization: Token <generated-token-value>
```

## Running tests

Run the automated test suite with:

```bash
python manage.py test
```

## Generating documentation with Sphinx

The project includes Sphinx documentation source files in the `docs` directory.

To rebuild the documentation:

```bash
python -m sphinx.ext.apidoc -o docs/source news_app
python -m sphinx -b html docs/source docs/build/html
```

The generated HTML documentation will be available in:

```text
docs/build/html
```

Open `index.html` in that folder to browse the generated docs.

## Known limitations

- The project is designed for learning and assessment, not production deployment.
- Email delivery is intended for local/demo use and may need configuration for real email services.
- Internal API logging assumes a local or controlled environment.
- The default MariaDB configuration requires local database setup before manual execution.

## Possible future improvements

- Add richer filtering and search for articles and newsletters
- Add profile management for subscribers
- Improve the approval audit trail
- Add pagination and throttling to API endpoints
- Add CI/CD automation for tests and documentation builds

## Contribution note

This repository was produced as part of an assessment task.  
If further changes are made, contributors should update the documentation, tests, and README
alongside any code changes so the repository remains consistent and easy to review.
