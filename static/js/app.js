let currentCompany = null;
let currentModels = [];


document.addEventListener("DOMContentLoaded", () => {

    loadCompanies();

    document
        .getElementById("search-input")
        .addEventListener("input", filterModels);

});

function renderModelTypes(models) {

    const typeList =
        document.getElementById("model-type-list");

    if (!typeList) {
        return;
    }

    typeList.innerHTML = "";

    if (!models || models.length === 0) {

        typeList.innerHTML = `
            <div class="filter-empty">
                No model types available.
            </div>
        `;

        return;
    }

    const typeCounts = {};

    models.forEach((model) => {

        const type =
            model.type || "LLM";

        typeCounts[type] =
            (typeCounts[type] || 0) + 1;
    });

    const modelTypes =
        Object.entries(typeCounts)
            .sort((a, b) => a[0].localeCompare(b[0]));

    modelTypes.forEach(([type, count]) => {

        const label =
            document.createElement("label");

        label.className = "filter-option";

        label.innerHTML = `
            <input
                type="checkbox"
                class="type-filter"
                value="${escapeHtml(type)}"
                checked
            >

            <span>
                ${escapeHtml(type)}
            </span>

            <small>
                ${count}
            </small>
        `;

        const checkbox =
            label.querySelector(".type-filter");

        checkbox.addEventListener(
            "change",
            filterModels
        );

        typeList.appendChild(label);
    });
}

async function loadCompanies() {

    const companyList = document.getElementById("company-list");

    companyList.innerHTML = `
        <div class="loading">
            Loading companies...
        </div>
    `;

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
                    src="${escapeHtml(company.logo)}"
                    alt="${escapeHtml(company.name)}"
                    onerror="this.style.display='none'; this.parentElement.textContent='AI'"
                >

                <span>${escapeHtml(company.name)}</span>

                <small>${company.model_count}</small>
            `;

            button.addEventListener("click", () => {
                loadCompanyModels(company.name, button);
            });

            companyList.appendChild(button);
        });

        if (companies.length > 0) {
            updateApiStatus(true);
        }

    } catch (error) {

        companyList.innerHTML = `
            <div class="error">
                Unable to load companies.
            </div>
        `;

        updateApiStatus(false);

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

        const modelList = document.getElementById("model-list");

        modelList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">◌</div>
                <h3>Loading models...</h3>
                <p>Fetching live models from OpenRouter.</p>
            </div>
        `;

        const response = await fetch(
            `/api/companies/${encodeURIComponent(companyName)}/models`
        );

        if (!response.ok) {
            throw new Error("Unable to load models");
        }

        const data = await response.json();

        currentCompany = companyName;
        currentModels = data.models;

        /*
        * Model types are derived ONLY from the
        * currently selected company's models.
        */
        renderModelTypes(currentModels);

        document.getElementById("models-title").textContent =
            `${companyName} Models`;

        document.getElementById("models-subtitle").textContent =
            `Live ${companyName} models available through OpenRouter.`;

        renderModels(currentModels);

    } catch (error) {

        console.error(error);

        document.getElementById("model-list").innerHTML = `
            <div class="error">
                Unable to load models from OpenRouter.
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

        const capabilities = Array.isArray(model.capabilities)
            ? model.capabilities
            : [];

        const modalities = Array.isArray(model.modalities)
            ? model.modalities
            : [];

        card.innerHTML = `
            <div class="model-card-header">

                <div class="model-icon">
                    ${getModelInitial(model.name)}
                </div>

                <span class="model-type">
                    ${escapeHtml(model.type || "LLM")}
                </span>

            </div>

            <h3>${escapeHtml(model.name)}</h3>

            <p class="model-id">
                ${escapeHtml(model.id)}
            </p>

            <div class="model-info">

                <div>
                    <span>Context</span>
                    <strong>${formatContext(model.context_length)}</strong>
                </div>

                <div>
                    <span>Launch Date</span>
                    <strong>${escapeHtml(model.launch_date || "N/A")}</strong>
                </div>

            </div>

            <div class="model-info">

                <div>
                    <span>Architecture</span>
                    <strong>${escapeHtml(model.architecture || "N/A")}</strong>
                </div>

                <div>
                    <span>Modalities</span>
                    <strong>
                        ${escapeHtml(
                            modalities.length
                                ? modalities.join(", ")
                                : "Text"
                        )}
                    </strong>
                </div>

            </div>

            <div class="capability-list">

                ${capabilities
                    .map(
                        (capability) =>
                            `<span>${escapeHtml(capability)}</span>`
                    )
                    .join("")}

            </div>

            <button
                class="details-button"
                data-model-id="${escapeHtml(model.id)}"
            >
                View Details →
            </button>
        `;

        const detailsButton =
            card.querySelector(".details-button");

        detailsButton.addEventListener("click", () => {
            showModelDetails(model.id);
        });

        modelList.appendChild(card);
    });
}


async function showModelDetails(modelId) {

    try {

        const details =
            document.getElementById("model-details");

        details.classList.remove("hidden");

        details.scrollIntoView({
            behavior: "smooth"
        });

        document.getElementById("detail-model-name").textContent =
            "Loading model details...";

        const response = await fetch(
            `/api/models/${encodeURIComponent(modelId)}`
        );

        if (!response.ok) {
            throw new Error("Unable to load model");
        }

        const data = await response.json();

        const model = data.model;

        const companyLogo =
            document.getElementById("detail-company-logo");

        if (companyLogo) {

            companyLogo.innerHTML = `
                <img
                    src="${escapeHtml(data.logo)}"
                    alt="${escapeHtml(data.company)}"
                    onerror="this.style.display='none'"
                >
            `;
        }

        const modelIcon =
            document.getElementById("detail-model-icon");

        if (modelIcon) {

            modelIcon.textContent =
                getModelInitial(model.name);
        }

        document.getElementById("detail-model-name").textContent =
            model.name;

        document.getElementById("detail-company").textContent =
            data.company;

        document.getElementById("detail-model-id").textContent =
            model.id;

        document.getElementById("detail-type").textContent =
            model.type;

        document.getElementById("detail-context").textContent =
            formatContext(model.context_length);

        document.getElementById("detail-architecture").textContent =
            model.architecture || "N/A";

        document.getElementById("detail-input-price").textContent =
            model.input_price || "N/A";

        document.getElementById("detail-output-price").textContent =
            model.output_price || "N/A";

        document.getElementById("detail-modalities").textContent =
            Array.isArray(model.modalities)
                ? model.modalities.join(", ")
                : "N/A";

        const launchDate =
            document.getElementById("detail-launch-date");

        if (launchDate) {
            launchDate.textContent =
                model.launch_date || "N/A";
        }

        const description =
            document.getElementById("detail-description");

        if (description) {
            description.textContent =
                model.description || "No description available.";
        }

        const inputModalities =
            document.getElementById("detail-input-modalities");

        if (inputModalities) {
            inputModalities.textContent =
                Array.isArray(model.input_modalities)
                    ? model.input_modalities.join(", ")
                    : "N/A";
        }

        const outputModalities =
            document.getElementById("detail-output-modalities");

        if (outputModalities) {
            outputModalities.textContent =
                Array.isArray(model.output_modalities)
                    ? model.output_modalities.join(", ")
                    : "N/A";
        }

        document.getElementById("detail-capabilities").innerHTML =
            (model.capabilities || [])
                .map(
                    (capability) =>
                        `<span>${escapeHtml(capability)}</span>`
                )
                .join("");

        const supportedParameters =
            document.getElementById(
                "detail-supported-parameters"
            );

        if (supportedParameters) {

            supportedParameters.innerHTML =
                (model.supported_parameters || [])
                    .map(
                        (parameter) =>
                            `<span>${escapeHtml(parameter)}</span>`
                    )
                    .join("");
        }

    } catch (error) {

        console.error(error);

        document.getElementById("detail-model-name").textContent =
            "Unable to load model";
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

            const modelName =
                (model.name || "").toLowerCase();

            const modelId =
                (model.id || "").toLowerCase();

            const matchesSearch =
                modelName.includes(searchTerm) ||
                modelId.includes(searchTerm);

            const matchesType =
                selectedTypes.length > 0 &&
                selectedTypes.includes(model.type);

            return matchesSearch && matchesType;
        });

    renderModels(filteredModels);
}

function getModelInitial(modelName) {

    if (!modelName) {
        return "AI";
    }

    const words =
        modelName
            .replace(/[:/()-]/g, " ")
            .split(/\s+/)
            .filter(Boolean);

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


function formatContext(contextLength) {

    if (!contextLength) {
        return "N/A";
    }

    const value = Number(contextLength);

    if (Number.isNaN(value)) {
        return contextLength;
    }

    if (value >= 1000000) {
        return `${(value / 1000000).toFixed(1)}M`;
    }

    if (value >= 1000) {
        return `${Math.round(value / 1000)}K`;
    }

    return value.toString();
}


function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function updateApiStatus(connected) {

    const status =
        document.querySelector(".status");

    if (!status) {
        return;
    }

    if (connected) {

        status.innerHTML = `
            <span class="status-dot"></span>
            OpenRouter Connected
        `;

    } else {

        status.innerHTML = `
            <span class="status-dot"></span>
            API Unavailable
        `;
    }
}