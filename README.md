# 🌍 Country Details API
A Django REST Framework project that provides an API to manage and retrieve country details. This project fetches country data from the [REST Countries API](https://restcountries.com/) and stores it in a local database.

---

## 🚀 Features
- ✅ List all countries
- ✅ Retrieve details of a specific country
- ✅ Filter countries by:
  - Same region
  - Language spoken
  - Search by name or official name
- ✅ CRUD operations for country data
- ✅ API-based views + HTML-based views
- ✅ Unit tests for API endpoints
- ✅ Code coverage reporting

---

## 🏗️ Project Structure
```
country_details_project/
├── countries_api/
│   ├── migrations/
│   ├── templates/
│   │   └── countries/
│   │       ├── same_region.html
│   │       ├── by_language.html
│   │       └── search_results.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests/
│   │   └── test_views.py
│   ├── urls.py
│   └── views.py
├── country_details_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

---

## ⚙️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/country-details-api.git
cd country-details-api
```

2. **Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Fetch and load country data:**
```bash
python manage.py fetch_countries
```

## 🏃 Running the server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/api/countries/ to access the API.

## ✅ Running Tests

Run the tests with Django's test runner:
```bash
python manage.py test
```

## 📊 Checking Code Coverage

1. Install coverage:
```bash
pip install coverage
```

2. Run tests with coverage:
```bash
coverage run manage.py test
```

3. Show coverage report in terminal:
```bash
coverage report
```

4. Generate an HTML coverage report:
```bash
coverage html
```
Open htmlcov/index.html in your browser to see the interactive coverage report.

## ✨ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/countries/ | List all countries |
| GET | /api/countries/{id}/ | Retrieve details of a country |
| GET | /api/countries/{id}/same_region/ | List countries in the same region |
| GET | /api/countries/by_language/ | Filter countries by language |
| GET | /api/countries/search/?q=term | Search countries by name |

## 🧪 Example Usage

Search for countries containing "United":
```http
GET /api/countries/search/?q=United
```

Get countries in the same region as country ID 1:
```http
GET /api/countries/1/same_region/
```

Filter countries by English language:
```http
GET /api/countries/by_language/?language=English
```

## 👨‍💻 Development Notes

- This project uses Django REST Framework's ModelViewSet.
- Custom actions are implemented using @action decorator.
- HTML templates are rendered using Django's render().
- All views are protected with authentication.

## 📄 License

This project is licensed under the MIT License.

## 🙌 Contributions

Contributions are welcome! Feel free to fork this repository, create a new branch, and submit a pull request.
