let currentCompany = null;
let currentModels = [];


document.addEventListener("DOMContentLoaded", () => {

    loadCompanies();

    document
        .getElementById("search-input")
        .addEventListener("input", filterModels);

    document
        .querySelectorAll(".type-filter")
        .forEach((checkbox) => {
            checkbox.addEventListener("change", filterModels);
        });
});


async function loadCompanies() {

    const companyList = document.getElementById("company-list");

    try {

        const response = await fetch("/api/companies");

        if (!response.ok) {
            throw new Error("Unable to load companies");
        }

        const companies = await response.json();

        companyList.innerHTML = "";

        companies.forEach((company) => {

            const button = document.createElement("button");

            button.className = "company-button";

            button.innerHTML = `
                <img
                    src="${company.logo}"
                    alt="${company.name}"
                    onerror="this.style.display='none'"
                >

                <span>${company.name}</span>

                <small>${company.model_count}</small>
            `;

            button.addEventListener("click", () => {
                loadCompanyModels(company.name, button);
            });

            companyList.appendChild(button);
        });

    } catch (error) {

        companyList.innerHTML = `
            <div class="error">
                Unable to load companies.
            </div>
        `;

        console.error(error);
    }
}


async function loadCompanyModels(companyName, button) {

    try {

        document
            .querySelectorAll(".company-button")
            .forEach((item) => {
                item.classList.remove("active");
            });

        button.classList.add("active");

        const response = await fetch(
            `/api/companies/${encodeURIComponent(companyName)}/models`
        );

        if (!response.ok) {
            throw new Error("Unable to load models");
        }

        const data = await response.json();

        currentCompany = companyName;
        currentModels = data.models;

        document.getElementById("models-title").textContent =
            `${companyName} Models`;

        document.getElementById("models-subtitle").textContent =
            `Explore ${companyName} foundation models and capabilities.`;

        renderModels(currentModels);

    } catch (error) {

        console.error(error);

        document.getElementById("model-list").innerHTML = `
            <div class="error">
                Unable to load models.
            </div>
        `;
    }
}


function renderModels(models) {

    const modelList = document.getElementById("model-list");
    const modelCount = document.getElementById("model-count");

    modelCount.textContent =
        `${models.length} model${models.length === 1 ? "" : "s"}`;

    if (models.length === 0) {

        modelList.innerHTML = `
            <div class="empty-state">
                <h3>No models found</h3>
                <p>Try changing your search or filters.</p>
            </div>
        `;

        return;
    }

    modelList.innerHTML = "";

    models.forEach((model) => {

        const card = document.createElement("div");

        card.className = "model-card";

        card.innerHTML = `
            <div class="model-card-header">

                <div class="model-icon">
                    ${getModelInitial(model.name)}
                </div>

                <span class="model-type">
                    ${model.type}
                </span>

            </div>

            <h3>${model.name}</h3>

            <p class="model-id">
                ${model.id}
            </p>

            <div class="model-info">

                <div>
                    <span>Context</span>
                    <strong>${model.context_length}</strong>
                </div>

                <div>
                    <span>Architecture</span>
                    <strong>${model.architecture}</strong>
                </div>

            </div>

            <div class="capability-list">

                ${model.capabilities
                    .map(
                        (capability) =>
                            `<span>${capability}</span>`
                    )
                    .join("")}

            </div>

            <button
                class="details-button"
                onclick="showModelDetails('${model.id}')"
            >
                View Details →
            </button>
        `;

        modelList.appendChild(card);
    });
}


async function showModelDetails(modelId) {

    try {

        const response = await fetch(
            `/api/models/${encodeURIComponent(modelId)}`
        );

        if (!response.ok) {
            throw new Error("Unable to load model");
        }

        const data = await response.json();

        const model = data.model;

        document.getElementById("detail-model-name").textContent =
            model.name;

        document.getElementById("detail-company").textContent =
            data.company;

        document.getElementById("detail-model-id").textContent =
            model.id;

        document.getElementById("detail-type").textContent =
            model.type;

        document.getElementById("detail-context").textContent =
            model.context_length;

        document.getElementById("detail-architecture").textContent =
            model.architecture;

        document.getElementById("detail-input-price").textContent =
            model.input_price;

        document.getElementById("detail-output-price").textContent =
            model.output_price;

        document.getElementById("detail-modalities").textContent =
            model.modalities.join(", ");

        document.getElementById("detail-capabilities").innerHTML =
            model.capabilities
                .map(
                    (capability) =>
                        `<span>${capability}</span>`
                )
                .join("");

        const details =
            document.getElementById("model-details");

        details.classList.remove("hidden");

        details.scrollIntoView({
            behavior: "smooth"
        });

    } catch (error) {

        console.error(error);

    }
}


function filterModels() {

    if (!currentCompany) {
        return;
    }

    const searchTerm =
        document
            .getElementById("search-input")
            .value
            .toLowerCase();

    const selectedTypes =
        Array.from(
            document.querySelectorAll(".type-filter:checked")
        ).map(
            (checkbox) => checkbox.value
        );

    const filteredModels =
        currentModels.filter((model) => {

            const matchesSearch =
                model.name
                    .toLowerCase()
                    .includes(searchTerm) ||
                model.id
                    .toLowerCase()
                    .includes(searchTerm);

            const matchesType =
                selectedTypes.length === 0 ||
                selectedTypes.includes(model.type);

            return matchesSearch && matchesType;
        });

    renderModels(filteredModels);
}


function getModelInitial(modelName) {

    const words = modelName.split(" ");

    if (words.length >= 2) {
        return (
            words[0][0] +
            words[1][0]
        ).toUpperCase();
    }

    return modelName
        .substring(0, 2)
        .toUpperCase();
}