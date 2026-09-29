from flask import Flask, jsonify, render_template

app = Flask(__name__)


MODEL_CATALOG = {
    "OpenAI": {
        "logo": "https://cdn.simpleicons.org/openai",
        "models": [
            {
                "id": "gpt-5",
                "name": "GPT-5",
                "type": "LLM",
                "context_length": "400K",
                "modalities": ["Text", "Image"],
                "capabilities": ["Reasoning", "Coding", "Tool Calling"],
                "architecture": "Transformer",
                "input_price": "$1.25 / 1M tokens",
                "output_price": "$10 / 1M tokens",
            },
            {
                "id": "gpt-4.1",
                "name": "GPT-4.1",
                "type": "LLM",
                "context_length": "1M",
                "modalities": ["Text", "Image"],
                "capabilities": ["Coding", "Reasoning", "Tool Calling"],
                "architecture": "Transformer",
                "input_price": "$2 / 1M tokens",
                "output_price": "$8 / 1M tokens",
            },
        ],
    },
    "Anthropic": {
        "logo": "https://cdn.simpleicons.org/anthropic",
        "models": [
            {
                "id": "claude-sonnet",
                "name": "Claude Sonnet",
                "type": "LLM",
                "context_length": "200K",
                "modalities": ["Text", "Image"],
                "capabilities": ["Reasoning", "Coding", "Tool Calling"],
                "architecture": "Transformer",
                "input_price": "$3 / 1M tokens",
                "output_price": "$15 / 1M tokens",
            }
        ],
    },
    "Google": {
        "logo": "https://cdn.simpleicons.org/google",
        "models": [
            {
                "id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "type": "LLM",
                "context_length": "1M",
                "modalities": ["Text", "Image", "Audio", "Video"],
                "capabilities": ["Reasoning", "Coding", "Multimodal"],
                "architecture": "Transformer",
                "input_price": "$1.25 / 1M tokens",
                "output_price": "$10 / 1M tokens",
            }
        ],
    },
    "Meta": {
        "logo": "https://cdn.simpleicons.org/meta",
        "models": [
            {
                "id": "llama-4",
                "name": "Llama 4",
                "type": "LLM",
                "context_length": "1M",
                "modalities": ["Text", "Image"],
                "capabilities": ["Reasoning", "Coding", "Multimodal"],
                "architecture": "MoE Transformer",
                "input_price": "Open Source",
                "output_price": "Open Source",
            }
        ],
    },
    "DeepSeek": {
        "logo": "https://cdn.simpleicons.org/deepseek",
        "models": [
            {
                "id": "deepseek-chat",
                "name": "DeepSeek Chat",
                "type": "LLM",
                "context_length": "128K",
                "modalities": ["Text"],
                "capabilities": ["Reasoning", "Coding"],
                "architecture": "MoE Transformer",
                "input_price": "$0.28 / 1M tokens",
                "output_price": "$0.42 / 1M tokens",
            }
        ],
    },
    "Mistral": {
        "logo": "https://cdn.simpleicons.org/mistral",
        "models": [
            {
                "id": "mistral-large",
                "name": "Mistral Large",
                "type": "LLM",
                "context_length": "128K",
                "modalities": ["Text"],
                "capabilities": ["Reasoning", "Coding", "Tool Calling"],
                "architecture": "Transformer",
                "input_price": "$2 / 1M tokens",
                "output_price": "$6 / 1M tokens",
            }
        ],
    },
    "Qwen": {
        "logo": "https://cdn.simpleicons.org/alibabacloud",
        "models": [
            {
                "id": "qwen3",
                "name": "Qwen3",
                "type": "LLM",
                "context_length": "128K",
                "modalities": ["Text"],
                "capabilities": ["Reasoning", "Coding", "Tool Calling"],
                "architecture": "Transformer",
                "input_price": "Open Source",
                "output_price": "Open Source",
            }
        ],
    },
}


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
    companies = []

    for company, data in MODEL_CATALOG.items():
        companies.append(
            {
                "name": company,
                "logo": data["logo"],
                "model_count": len(data["models"]),
            }
        )

    return jsonify(companies)


@app.route("/api/companies/<company>/models")
def get_company_models(company):
    company_data = MODEL_CATALOG.get(company)

    if not company_data:
        return jsonify({"error": "Company not found"}), 404

    return jsonify(
        {
            "company": company,
            "logo": company_data["logo"],
            "models": company_data["models"],
        }
    )


@app.route("/api/models/<model_id>")
def get_model(model_id):
    for company, data in MODEL_CATALOG.items():
        for model in data["models"]:
            if model["id"] == model_id:
                return jsonify(
                    {
                        "company": company,
                        "logo": data["logo"],
                        "model": model,
                    }
                )

    return jsonify({"error": "Model not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
