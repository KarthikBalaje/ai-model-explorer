import os
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODELS_URL = f"{OPENROUTER_BASE_URL}/models"


# Providers that we want to display in the AI Model Explorer.
# Model versions themselves come dynamically from OpenRouter.
PROVIDER_CONFIG = {
    "OpenAI": {
        "logo": "https://api.iconify.design/simple-icons:openai.svg",
        "prefixes": ["openai/"],
    },
    "Anthropic": {
        "logo": "https://api.iconify.design/simple-icons:anthropic.svg",
        "prefixes": ["anthropic/"],
    },
    "Google": {
        "logo": "https://api.iconify.design/simple-icons:google.svg",
        "prefixes": ["google/"],
    },
    "Meta": {
        "logo": "https://api.iconify.design/simple-icons:meta.svg",
        "prefixes": ["meta-llama/", "meta/"],
    },
    "DeepSeek": {
        "logo": "https://api.iconify.design/simple-icons:deepseek.svg",
        "prefixes": ["deepseek/"],
    },
    "Mistral": {
        "logo": "https://api.iconify.design/simple-icons:mistral.svg",
        "prefixes": ["mistralai/"],
    },
    "Qwen": {
        "logo": "https://api.iconify.design/simple-icons:alibabacloud.svg",
        "prefixes": ["qwen/"],
    },
}


def get_openrouter_headers():
    """Return headers required for OpenRouter requests."""

    headers = {
        "Accept": "application/json",
    }

    if OPENROUTER_API_KEY:
        headers["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"

    return headers


def detect_provider(model_id):
    """Map an OpenRouter model ID to one of our displayed companies."""

    model_id = model_id.lower()

    for company, config in PROVIDER_CONFIG.items():
        for prefix in config["prefixes"]:
            if model_id.startswith(prefix):
                return company

    return None


def format_price(price):
    """Convert OpenRouter pricing into a readable value."""

    if price is None:
        return "N/A"

    try:
        value = float(price)

        if value == 0:
            return "Free"

        # OpenRouter pricing is commonly represented per token.
        per_million = value * 1_000_000

        return f"${per_million:.4f} / 1M tokens"

    except (TypeError, ValueError):
        return str(price)


def format_date(timestamp):
    """Convert Unix timestamp to YYYY-MM-DD."""

    if not timestamp:
        return "N/A"

    try:
        return datetime.fromtimestamp(
            int(timestamp),
            tz=timezone.utc,
        ).strftime("%Y-%m-%d")

    except (TypeError, ValueError, OverflowError):
        return "N/A"

def infer_model_type(model):
    """Infer model type from OpenRouter model metadata."""

    architecture = model.get("architecture") or {}

    input_modalities = architecture.get("input_modalities") or []
    output_modalities = architecture.get("output_modalities") or []

    modalities = {
        str(modality).lower()
        for modality in input_modalities + output_modalities
    }

    model_id = model.get("id", "").lower()
    name = model.get("name", "").lower()

    combined_name = f"{model_id} {name}"

    # Embedding models
    if (
        "embedding" in combined_name
        or "embed" in combined_name
    ):
        return "Embedding"

    # Explicit multimodal capability
    multimodal_modalities = {
        "image",
        "audio",
        "video",
        "file",
    }

    if modalities.intersection(multimodal_modalities):
        return "Multimodal"

    # Smaller model families / SLM indicators
    slm_indicators = [
        "0.5b",
        "0.6b",
        "1b",
        "1.5b",
        "2b",
        "3b",
        "4b",
        "7b",
        "8b",
        "mini",
        "small",
        "tiny",
        "nano",
        "micro",
    ]

    if any(indicator in combined_name for indicator in slm_indicators):
        return "SLM"

    # Default text-generation model
    return "LLM"

def build_capabilities(model):
    """Build user-friendly capabilities from OpenRouter metadata."""

    capabilities = []

    supported_parameters = model.get("supported_parameters") or []

    parameter_map = {
        "reasoning": "Reasoning",
        "tools": "Tool Calling",
        "tool_choice": "Tool Calling",
        "structured_outputs": "Structured Outputs",
        "response_format": "Structured Outputs",
        "temperature": "Temperature Control",
    }

    for parameter in supported_parameters:
        capability = parameter_map.get(parameter)

        if capability and capability not in capabilities:
            capabilities.append(capability)

    architecture = model.get("architecture") or {}

    input_modalities = architecture.get("input_modalities") or []

    if "image" in input_modalities:
        capabilities.append("Vision")

    if "audio" in input_modalities:
        capabilities.append("Audio")

    if "video" in input_modalities:
        capabilities.append("Video")

    if not capabilities:
        capabilities.append("Text Generation")

    return capabilities


def normalize_model(model):
    """Convert an OpenRouter model into the UI's model format."""

    model_id = model.get("id", "")

    company = detect_provider(model_id)

    if not company:
        return None

    architecture = model.get("architecture") or {}

    input_modalities = architecture.get("input_modalities") or []
    output_modalities = architecture.get("output_modalities") or []

    modalities = []

    for modality in input_modalities + output_modalities:
        formatted = str(modality).replace("_", " ").title()

        if formatted not in modalities:
            modalities.append(formatted)

    pricing = model.get("pricing") or {}

    return {
        "id": model_id,
        "name": model.get("name") or model_id,
        "type": infer_model_type(model),
        "context_length": model.get("context_length") or "N/A",
        "modalities": modalities,
        "input_modalities": input_modalities,
        "output_modalities": output_modalities,
        "capabilities": build_capabilities(model),
        "architecture": architecture.get("modality") or "N/A",
        "input_price": format_price(pricing.get("prompt")),
        "output_price": format_price(pricing.get("completion")),
        "launch_date": format_date(model.get("created")),
        "description": model.get("description") or "No description available.",
        "supported_parameters": model.get("supported_parameters") or [],
        "raw": model,
    }


def fetch_openrouter_models():
    """Fetch the current model catalog from OpenRouter."""

    response = requests.get(
        OPENROUTER_MODELS_URL,
        headers=get_openrouter_headers(),
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    return payload.get("data", [])


def get_normalized_models():
    """Fetch and normalize supported models."""

    models = fetch_openrouter_models()

    normalized = []

    for model in models:
        normalized_model = normalize_model(model)

        if normalized_model:
            normalized.append(normalized_model)

    return normalized


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "service": "AI Model Explorer",
        }
    )


@app.route("/api/companies")
def get_companies():

    try:
        models = get_normalized_models()

        companies = []

        for company, config in PROVIDER_CONFIG.items():

            company_models = [
                model
                for model in models
                if detect_provider(model["id"]) == company
            ]

            if company_models:
                companies.append(
                    {
                        "name": company,
                        "logo": config["logo"],
                        "model_count": len(company_models),
                    }
                )

        return jsonify(companies)

    except requests.RequestException as error:

        return jsonify(
            {
                "error": "Unable to fetch model catalog from OpenRouter",
                "details": str(error),
            }
        ), 502

@app.route("/api/companies/<company>/models")
def get_company_models(company):

    if company not in PROVIDER_CONFIG:
        return jsonify({"error": "Company not found"}), 404

    try:

        models = get_normalized_models()

        company_models = [
            model
            for model in models
            if detect_provider(model["id"]) == company
        ]

        return jsonify(
            {
                "company": company,
                "logo": PROVIDER_CONFIG[company]["logo"],
                "models": company_models,
            }
        )

    except requests.RequestException as error:

        return jsonify(
            {
                "error": "Unable to fetch models from OpenRouter",
                "details": str(error),
            }
        ), 502


@app.route("/api/models/<path:model_id>")
def get_model(model_id):

    try:

        models = get_normalized_models()

        for model in models:

            if model["id"] == model_id:

                company = detect_provider(model["id"])

                return jsonify(
                    {
                        "company": company,
                        "logo": PROVIDER_CONFIG[company]["logo"],
                        "model": model,
                    }
                )

        return jsonify({"error": "Model not found"}), 404

    except requests.RequestException as error:

        return jsonify(
            {
                "error": "Unable to fetch model from OpenRouter",
                "details": str(error),
            }
        ), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )