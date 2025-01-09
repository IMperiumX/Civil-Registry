
# Egyptian National ID Validator API

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
* Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:

    ```bash
    git clone git@github.com/imperiumx/civil_registry.git
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

4. Set up the database (using SQLite by default):

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Create a superuser (to access Django admin and generate API keys):

    ```bash
    python manage.py createsuperuser
    ```

## Running the Application

```bash
python manage.py runserver
```

The API will be accessible at `http://127.0.0.1:8000/`.

## API Endpoint

**POST /api/national-id/**

**Request Headers:**

* `Authorization`: `Token <your_api_key>`

**Request Body (JSON):**

```json
{
  "national_id": "29001011234567"
}
```

**Response (200 OK):**

```json
{
  "is_valid": true,
  "id_number": "23301011294197",
  "birth_date": "1933-01-01",
  "governorate": "Dakahlia",
  "gender": "Male",
  "detail": ""
}
```

**Response (400 Bad Request):**

```json
{
  "national_id": [
    "This field must be 14 digits."
  ]
}
```

**Response (400 Bad Request - Invalid ID):**

```json
{
  "is_valid": false,
  "id_number": "123301011294197",
  "detail": "National ID must be a 14-digit number."
}
```

## API Key Generation

1. Log in to the Django admin panel (`http://127.0.0.1:8000/admin/`).
2. Go to "Tokens" and create a new token for a user.
3. Copy the generated token key and use it in the `Authorization` header for API requests.

## Notes

* The governorate extraction logic needs to be completed with a proper mapping of codes to governorate names.
* You can adjust the rate limiting in `settings.py`.
* For production, consider using a more robust database like PostgreSQL or MySQL.
* For enhanced security, you could create a custom `APIKey` model (instead of DRF's `Token`) with features like key expiry, usage limits, etc.

## Testing

```bash
python manage.py test civil_registery
```

Make sure the development server is not running when executing the tests.
