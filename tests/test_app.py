import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["service"] == "AI Model Explorer"


def test_companies_endpoint(client):
    response = client.get("/api/companies")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0

    company_names = [company["name"] for company in data]

    assert "OpenAI" in company_names
    assert "Anthropic" in company_names
    assert "Google" in company_names


def test_openai_models_endpoint(client):
    response = client.get("/api/companies/OpenAI/models")

    assert response.status_code == 200

    data = response.get_json()

    assert data["company"] == "OpenAI"
    assert len(data["models"]) > 0


def test_model_details_endpoint(client):
    response = client.get("/api/models/gpt-5")

    assert response.status_code == 200

    data = response.get_json()

    assert data["company"] == "OpenAI"
    assert data["model"]["id"] == "gpt-5"


def test_invalid_company(client):
    response = client.get("/api/companies/InvalidCompany/models")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Company not found"


def test_invalid_model(client):
    response = client.get("/api/models/invalid-model")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Model not found"
