import pytest

from app import app

MOCK_OPENROUTER_MODELS = [
    {
        "id": "openai/gpt-5",
        "name": "OpenAI: GPT-5",
        "created": 1751328000,
        "description": "Mock GPT-5 model for unit testing.",
        "context_length": 400000,
        "architecture": {
            "modality": "text+image->text",
            "input_modalities": ["text", "image"],
            "output_modalities": ["text"],
        },
        "pricing": {
            "prompt": "0.00000125",
            "completion": "0.00001",
        },
        "supported_parameters": [
            "reasoning",
            "tools",
            "structured_outputs",
        ],
    },
    {
        "id": "anthropic/claude-sonnet",
        "name": "Anthropic: Claude Sonnet",
        "created": 1751328000,
        "description": "Mock Claude model for unit testing.",
        "context_length": 200000,
        "architecture": {
            "modality": "text+image->text",
            "input_modalities": ["text", "image"],
            "output_modalities": ["text"],
        },
        "pricing": {
            "prompt": "0.000003",
            "completion": "0.000015",
        },
        "supported_parameters": [
            "tools",
            "structured_outputs",
        ],
    },
    {
        "id": "google/gemini-test",
        "name": "Google: Gemini Test",
        "created": 1751328000,
        "description": "Mock Gemini model for unit testing.",
        "context_length": 1000000,
        "architecture": {
            "modality": "text+image+audio->text",
            "input_modalities": [
                "text",
                "image",
                "audio",
            ],
            "output_modalities": ["text"],
        },
        "pricing": {
            "prompt": "0.000001",
            "completion": "0.000008",
        },
        "supported_parameters": [
            "tools",
        ],
    },
]


class MockOpenRouterResponse:
    """Minimal response object used to mock OpenRouter."""

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "data": MOCK_OPENROUTER_MODELS,
        }


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_openrouter(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockOpenRouterResponse()

    monkeypatch.setattr(
        "app.requests.get",
        mock_get,
    )


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["service"] == "AI Model Explorer"


def test_companies_endpoint(client, mock_openrouter):
    response = client.get("/api/companies")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0

    company_names = [company["name"] for company in data]

    assert "OpenAI" in company_names
    assert "Anthropic" in company_names
    assert "Google" in company_names


def test_openai_models_endpoint(client, mock_openrouter):
    response = client.get("/api/companies/OpenAI/models")

    assert response.status_code == 200

    data = response.get_json()

    assert data["company"] == "OpenAI"
    assert len(data["models"]) > 0

    model = data["models"][0]

    assert model["id"] == "openai/gpt-5"
    assert model["name"] == "OpenAI: GPT-5"
    assert model["context_length"] == 400000
    assert model["type"] == "Multimodal"
    assert "Vision" in model["capabilities"]


def test_model_details_endpoint(client, mock_openrouter):
    response = client.get("/api/models/openai/gpt-5")

    assert response.status_code == 200

    data = response.get_json()

    assert data["company"] == "OpenAI"

    assert data["model"]["id"] == "openai/gpt-5"

    assert data["model"]["name"] == "OpenAI: GPT-5"

    assert data["model"]["launch_date"] != "N/A"

    assert data["model"]["context_length"] == 400000

    assert "Vision" in data["model"]["capabilities"]


def test_invalid_company(client):
    response = client.get("/api/companies/InvalidCompany/models")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Company not found"


def test_invalid_model(client, mock_openrouter):
    response = client.get("/api/models/invalid-model")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Model not found"
