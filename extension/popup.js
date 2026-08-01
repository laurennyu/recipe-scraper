const saveButton = document.getElementById("saveButton");
const closeButton = document.getElementById("closeButton");
const statusMessage = document.getElementById("statusMessage");
const previewBox = document.getElementById("previewBox");
const previewTitle = document.getElementById("previewTitle");
const previewIngredients = document.getElementById("previewIngredients");
const previewInstructions = document.getElementById("previewInstructions");
const previewMeta = document.getElementById("previewMeta");
const contentPanel = document.getElementById("contentPanel");
const metadataForm = document.getElementById("metadataForm");
const triedCheckbox = document.getElementById("triedCheckbox");
const ratingSelect = document.getElementById("ratingSelect");
const notesInput = document.getElementById("notesInput");
const tagGroup = document.getElementById("tagGroup");

let previewedRecipe = null;
let selectedTags = [];

closeButton.addEventListener("click", () => {
    window.close();
});

function displayText(value) {
    return value === null || value === undefined ? "" : String(value).trim();
}

function ingredientParts(ingredient) {
    const amountText = displayText(ingredient?.amount_text)
        || [displayText(ingredient?.quantity), displayText(ingredient?.unit)]
            .filter(Boolean)
            .join(" ");
    const name = displayText(ingredient?.name);

    return { amountText, name };
}

function renderIngredient(item, ingredient) {
    const { amountText, name } = ingredientParts(ingredient);

    if (!amountText && !name) {
        item.textContent = "Unknown ingredient";
        return;
    }

    if (amountText) {
        item.append(document.createTextNode(name ? `${amountText} ` : amountText));
    }

    if (name) {
        const nameElement = document.createElement("span");
        nameElement.className = "ingredientName";
        nameElement.textContent = name;
        item.append(nameElement);
    }
}

function renderPreview(recipe) {
    contentPanel.hidden = false;
    previewBox.hidden = false;
    previewTitle.textContent = recipe?.title || "Untitled recipe";
    previewIngredients.innerHTML = "";
    previewInstructions.innerHTML = "";

    const ingredients = recipe?.ingredients || [];
    if (ingredients.length > 0) {
        ingredients.forEach((ingredient) => {
            const item = document.createElement("li");
            renderIngredient(item, ingredient);
            previewIngredients.appendChild(item);
        });
    } else {
        const item = document.createElement("li");
        item.textContent = "No ingredients were found.";
        previewIngredients.appendChild(item);
    }

    const instructions = recipe?.instructions || [];
    if (instructions.length > 0) {
        instructions.forEach((instruction) => {
            const item = document.createElement("li");
            item.textContent = instruction;
            previewInstructions.appendChild(item);
        });
    } else {
        const item = document.createElement("li");
        item.textContent = "No instructions were found.";
        previewInstructions.appendChild(item);
    }

    const metaParts = [];
    if (recipe?.total_time) {
        metaParts.push(`Time: ${recipe.total_time}`);
    }
    if (recipe?.yields) {
        metaParts.push(`Yields: ${recipe.yields}`);
    }
    previewMeta.textContent = metaParts.join(" • ");
}

function recipeWithReviewFields(recipe) {
    const rating = ratingSelect.value;

    return {
        ...recipe,
        tried: triedCheckbox.checked,
        rating: rating ? Number(rating) : null,
        tags: selectedTags.length > 0 ? selectedTags.join(", ") : null,
        notes: notesInput.value.trim() || null
    };
}

tagGroup.addEventListener("click", (event) => {
    const chip = event.target.closest(".tagChip");
    if (!chip) {
        return;
    }

    const tag = chip.dataset.tag;
    if (!tag) {
        return;
    }

    chip.classList.toggle("active");

    if (selectedTags.includes(tag)) {
        selectedTags = selectedTags.filter((item) => item !== tag);
    } else {
        selectedTags = [...selectedTags, tag];
    }
});

saveButton.addEventListener("click", async () => {
    saveButton.disabled = true;
    saveButton.textContent = "Working...";
    statusMessage.textContent = previewedRecipe ? "Saving recipe..." : "Parsing recipe...";

    try {
        const [tab] = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

        if (!tab?.id) {
            throw new Error("No active tab found.");
        }

        const action = previewedRecipe ? "saveRecipe" : "previewRecipe";
        const recipeToSave = previewedRecipe ? recipeWithReviewFields(previewedRecipe) : null;
        const response = await chrome.tabs.sendMessage(
            tab.id,
            recipeToSave ? { action, recipe: recipeToSave } : { action }
        );

        if (response?.recipe) {
            if (!previewedRecipe) {
                previewedRecipe = response.recipe;
                renderPreview(previewedRecipe);
                saveButton.textContent = "Save Recipe";
                statusMessage.textContent = "Preview ready. Click save to store it.";
            } else {
                previewedRecipe = recipeToSave;
                saveButton.textContent = "Saved";
                statusMessage.textContent = "Recipe saved to storage.";
            }
        } else {
            throw new Error("No recipe data received.");
        }
    } catch (error) {
        statusMessage.textContent = "Unable to process recipe.";
        saveButton.textContent = previewedRecipe ? "Save Recipe" : "Preview Recipe";
    } finally {
        saveButton.disabled = false;
    }
});
