
# Egyptian National ID Validator API

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This is a Django REST Framework API for validating and extracting information from Egyptian National IDs.

## Features

* **Validation:** Checks if a given Egyptian National ID is valid.
* **Data Extraction:** Extracts birth date, governorate, and gender from valid National IDs.
* **Rate Limiting:** Implements rate limiting to prevent abuse (default: 100 requests/day per user).
* **API Key Authentication:** Uses API keys to authenticate requests.
* **Request Tracking:** Logs all API requests for monitoring and analysis.

## Requirements

* Python 3.11+
* Django 5.0+
* Django REST Framework 3.15+
* Other dependencies listed in `requirements`

## Installation

1. Clone the repository:

    ```bash
    git clone git@github.com:IMperiumX/civil-registry.git
    cd civil_registry
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv env
    source env/bin/activate  # On macOS/Linux
    env\Scripts\activate  # On Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements/local.txt
    ```

4. Create a new PostgreSQL database using `createdb`:

    ```bash
    createdb --username=postgres <DB name>
    ```

    > [!NOTE]
      if this is the first time a database is created on your machine you might need an [initial PostgreSQL set](https://web.archive.org/web/20190303010033/http://suite.opengeo.org/docs/latest/dataadmin/pgGettingStarted/firstconnect.html) up to allow local connections & set a password for the `postgres` user. The [postgres documentation](https://www.postgresql.org/docs/current/static/auth-pg-hba-conf.html) explains the syntax of the config file that you need to change.

5. Set the environment variables for your database(s):

    ```bash
    export DATABASE_URL=postgres://postgres:<password>@127.0.0.1:5432/<DB name given to createdb>
    ```

    **OR**

    ```bash
    cp .env.sample .env
    ```

    > [!NOTE]
      To help setting up your environment variables, you have a few options:
      create an `.env` file in the root of your project and define all the variables you need in it. Then you just need to have `DJANGO_READ_DOT_ENV_FILE=True` in your machine and all the variables will be read.
      Use a local environment manager like [direnv](https://direnv.net/)

6. Apply migrations:

    ```bash
    python manage.py migrate
    ```

7. Start Django development server:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

   The API will be accessible at `http://127.0.0.1:8000/api/docs`.

8. Create a superuser (to access Django admin and generate API keys):

    ```bash
    python manage.py createsuperuser
    ```

## API Endpoint

## POST /api/validate/

**Request Headers:**

* `Authorization`: `Token <your_api_key>`

**Request Body (JSON):**

```json
{
  "id_number": "29001011234567"
}
```

**Response (200 OK):**

```json
{
  "is_valid": true,
  "id_number": "29001011234567",
  "birth_date": "1990-01-01",
  "governorate": "Dakahlia",
  "gender": "Female",
  "detail": ""
}
```

**Response (400 Bad Request):**

```json
{
  "is_valid": false,
  "id_number": "932028345643771",
  "detail": "National ID must be a 14-digit number."
}
```

**Response (400 Bad Request - Invalid ID):**

```json
{
  "is_valid": false,
  "id_number": "290010112345671",
  "detail": "National ID must be a 14-digit number."
}
```

## API Key Generation

### POST /api/auth-token/

**Request Body (JSON):**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**

```json
{
  "token": "<drf_token>"
}
```

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

```bash
coverage run -m pytest
coverage html
open htmlcov/index.html
```

#### Running tests with pytest

```bash
pytest
```

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd civil_registry
celery -A config.celery_app worker -l info
```

> [!NOTE]
  Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.
