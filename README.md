# CVProject - Django Developer Practical Test

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.4+-green.svg)
![Poetry](https://img.shields.io/badge/poetry-dependency--management-blue.svg)

## 📋 Requirements

- Follow **PEP 8** and other style guidelines
- Use clear and concise commit messages and docstrings where needed
- Structure your project for readability and maintainability
- Optimize database access using Django's built-in methods
- Provide enough details in your README

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pyenv
- Poetry

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd CVProject
   ```
2. **Set up Python environment**

   ```bash
   pyenv install 3.11.0
   pyenv local 3.11.0
   ```
3. **Install dependencies with Poetry**

   ```bash
   poetry install
   poetry shell
   ```
4. **Run the application**

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## 🧪 Testing

To run the tests:

```bash
python manage.py test
```

## 📁 Project Structure

```
CVProject/
├── src/
│   └── cvproject/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
├── poetry.lock
└── README.md
```

## 📝 Version Control System

1. **Create a public GitHub repository** for this practical test (e.g., `DTEAM-django-practical-test`)
2. **Put the text of this test** (all instructions) into `README.md`
3. **For each task, create a separate branch** (e.g., `tasks/task-1`, `tasks/task-2`, etc.)
4. **When you finish each task**, merge that branch back into `main` but do not delete the original task branch

## 🛠️ Python Virtual Environment

5. **Use pyenv** to manage the Python version. Create a file named `.python-version` in your repository to store the exact Python version
6. **Use Poetry** to manage and store project dependencies. This will create a `pyproject.toml` file
7. **Update your README.md** with clear instructions on how to set up and use pyenv and Poetry for this project

## 📚 Tasks

### Task 1: Django Fundamentals

8. **Create a New Django Project**

   - Name it something like `CVProject`
   - Use the Python version set up in Task 2 and the latest stable Django release
   - Use SQLite as your database for now
9. **Create an App and Model**

   - Create a Django app (e.g., `main`)
   - Define a CV model with fields like `firstname`, `lastname`, `skills`, `projects`, `bio`, and `contacts`
   - Organize the data in a way that feels efficient and logical
10. **Load Initial Data with Fixtures**

    - Create a fixture that contains at least one sample CV instance
    - Include instructions in `README.md` on how to load the fixture
11. **List Page View and Template**

    - Implement a view for the main page (e.g., `/`) to display a list of CV entries
    - Use any CSS library to style them nicely
    - Ensure the data is retrieved from the database efficiently
12. **Detail Page View**

    - Implement a detail view (e.g., `/cv/<id>/`) to show all data for a single CV
    - Style it nicely and ensure efficient data retrieval
13. **Tests**

    - Add basic tests for the list and detail views
    - Update `README.md` with instructions on how to run these tests

### Task 2: PDF Generation Basics

14. **Choose and install** any HTML-to-PDF generating library or tool
15. **Add a 'Download PDF' button** on the CV detail page that allows users to download the CV as a PDF

### Task 3: REST API Fundamentals

16. **Install Django REST Framework** (DRF)
17. **Create CRUD endpoints** for the CV model (create, retrieve, update, delete)
18. **Add tests** to verify that each CRUD action works correctly

### Task 4: Middleware & Request Logging

19. **Create a RequestLog Model**

    - You can put this in the existing app or a new app (e.g., `audit`)
    - Include fields such as timestamp, HTTP method, path, and optionally other details like query string, remote IP, or logged-in user
20. **Implement Logging Middleware**

    - Write a custom Django middleware class that intercepts each incoming request
    - Create a RequestLog record in the database with the relevant request data
    - Keep it efficient
21. **Recent Requests Page**

    - Create a view (e.g., `/logs/`) showing the 10 most recent logged requests, sorted by timestamp descending
    - Include a template that loops through these entries and displays their timestamp, method, and path
22. **Test Logging**

    - Ensure your tests verify the logging functionality

### Task 5: Template Context Processors

23. **Create settings_context**

    - Create a context processor that injects your entire Django settings into all templates
24. **Settings Page**

    - Create a view (e.g., `/settings/`) that displays DEBUG and other settings values made available by the context processor

### Task 6: Docker Basics

25. **Use Docker Compose** to containerize your project
26. **Switch the database** from SQLite to PostgreSQL in Docker Compose
27. **Store all necessary environment variables** (database credentials, etc.) in a `.env` file

### Task 7: Celery Basics

28. **Install and configure Celery**, using Redis or RabbitMQ as the broker
29. **Add a Celery worker** to your Docker Compose configuration
30. **On the CV detail page**, add an email input field and a 'Send PDF to Email' button to trigger a Celery task that emails the PDF

### Task 8: OpenAI Basics

31. **On the CV detail page**, add a 'Translate' button and a language selector
32. **Include these languages**: Cornish, Manx, Breton, Inuktitut, Kalaallisut, Romani, Occitan, Ladino, Northern Sami, Upper Sorbian, Kashubian, Zazaki, Chuvash, Livonian, Tsakonian, Saramaccan, Bislama
33. **Hook this up to an OpenAI translation API** or any other translation mechanism you prefer. The idea is to translate the CV content into the selected language

### Task 9: Deployment

34. **Deploy this project** to DigitalOcean or any other VPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is for educational purposes as part of the DTEAM Django Developer Practical Test.

# CV Project

A Django-based CV management system with REST API functionality, built with Docker and Celery.

## Features

- CV management with CRUD operations
- REST API endpoints
- Request logging middleware
- Template context processors
- Celery for asynchronous tasks (PDF generation and email sending)
- PostgreSQL database
- Redis for Celery broker
- Docker containerization

## Setup and Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your environment variables
3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

## Loading Initial Data

The project includes fixture files with sample data to help you get started quickly.

### Using Fixtures

To load the initial data (sample CVs and skills), run the following command:

```bash
docker-compose exec web python manage.py loaddata fixtures/initial_data.json
```

This will create:

- Sample skills (Python, Django, JavaScript, React, PostgreSQL, Docker, Node.js, Vue.js)
- 3 sample CV records with different professional profiles
- Relationships between CVs and their associated skills

### Manual Data Management

You can also manage data manually through:

- Django Admin interface: `http://localhost:8000/admin/`
- API endpoints: `http://localhost:8000/api/cvs/`
- Django shell: `docker-compose exec web python manage.py shell`

### Creating Custom Fixtures

To create your own fixtures from existing data:

```bash
# Export all CV data
docker-compose exec web python manage.py dumpdata main.CV --indent 2 > fixtures/cvs.json
```

## API Endpoints

- `GET/POST /api/cvs/` - List all CVs / Create new CV
- `GET/PUT/PATCH/DELETE /api/cvs/{id}/` - Retrieve/Update/Delete specific CV
- `GET/cv/{id}/` **CV Detail** View with sending email functionality

## Additional Features

- **Request Logs**: View at `/logs/`
- **Settings Page**: View at `/settings/`
- **Send CV PDF**: Use the email form on CV detail pages

## Development

Access the services:

- Web application: `http://localhost:8000`
- PostgreSQL: `localhost:5433`
- Redis: `localhost:6380`

View logs:

```bash
docker-compose logs web
docker-compose logs celery
```
