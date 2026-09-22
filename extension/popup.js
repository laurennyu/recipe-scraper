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
const accountForm = document.getElementById("accountForm");
const accountSelect = document.getElementById("accountSelect");
const activeAccount = document.getElementById("activeAccount");
const activeAccountName = document.getElementById("activeAccountName");
const changeAccountButton = document.getElementById("changeAccountButton");
const accountChooser = document.getElementById("accountChooser");
const addAccountButton = document.getElementById("addAccountButton");
const newAccountFields = document.getElementById("newAccountFields");
const usernameInput = document.getElementById("usernameInput");
const accountHint = document.getElementById("accountHint");

let previewedRecipe = null;
let selectedTags = [];
let activeUsername = "";

function setAddingAccount(isAdding) {
    newAccountFields.hidden = !isAdding;
    usernameInput.disabled = !isAdding;
    usernameInput.required = isAdding;
    addAccountButton.hidden = isAdding;
    if (isAdding) {
        usernameInput.value = "";
        usernameInput.focus();
    }
}

function updateAccountUI() {
    const hasAccount = Boolean(activeUsername);
    activeAccount.hidden = !hasAccount;
    accountChooser.hidden = hasAccount;
    activeAccountName.textContent = hasAccount ? `Saving as ${activeUsername}` : "";
    if (!hasAccount) setAddingAccount(false);
}

async function loadAccounts() {
    const response = await fetch("http://localhost:8000/api/users");
    if (!response.ok) throw new Error("Could not load accounts.");
    const users = await response.json();
    accountSelect.replaceChildren(new Option("Choose account", ""));
    users.forEach((user) => accountSelect.add(new Option(user.username, user.username)));
    accountSelect.value = activeUsername;
}

async function useAccount(username) {
    const response = await fetch(`http://localhost:8000/api/users/select?username=${encodeURIComponent(username)}`, { method: "POST" });
    const account = await response.json();
    if (!response.ok) throw new Error(account.detail || "Could not select account.");
    activeUsername = account.username;
    localStorage.setItem("recipeSaverUsername", activeUsername);
    usernameInput.value = activeUsername;
    accountHint.textContent = `Saving recipes to ${activeUsername}'s account.`;
    await loadAccounts();
    updateAccountUI();
}

accountForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
        await useAccount(usernameInput.value);
    } catch (error) {
        accountHint.textContent = error.message || "Could not select account.";
    }
});

accountSelect.addEventListener("change", async () => {
    if (!accountSelect.value) return;
    try {
        await useAccount(accountSelect.value);
    } catch (error) {
        accountHint.textContent = error.message || "Could not switch account.";
    }
});

addAccountButton.addEventListener("click", () => setAddingAccount(true));
changeAccountButton.addEventListener("click", () => {
    accountChooser.hidden = false;
    activeAccount.hidden = true;
    setAddingAccount(false);
    accountSelect.focus();
});

(async () => {
    activeUsername = localStorage.getItem("recipeSaverUsername") || "";
    usernameInput.value = activeUsername;
    updateAccountUI();
    if (activeUsername) accountHint.textContent = `Saving recipes to ${activeUsername}'s account.`;
    try {
        await loadAccounts();
    } catch {
        accountHint.textContent = "Start the local server to choose an account.";
    }
})();

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
    if (previewedRecipe && !activeUsername) {
        statusMessage.textContent = "Choose an account before saving.";
        return;
    }
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

        const recipeToSave = previewedRecipe ? recipeWithReviewFields(previewedRecipe) : null;
        let response;
        if (recipeToSave) {
            const saveResponse = await fetch(
                `http://localhost:8000/save?username=${encodeURIComponent(activeUsername)}`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Recipe-Username": activeUsername
                    },
                    body: JSON.stringify(recipeToSave)
                }
            );
            const data = await saveResponse.json();
            if (!saveResponse.ok) throw new Error(data.detail || "Could not save recipe.");
            response = { recipe: data.recipe };
        } else {
            response = await chrome.tabs.sendMessage(tab.id, { action: "previewRecipe" });
        }

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
            throw new Error(response?.error || "No recipe data received.");
        }
    } catch (error) {
        statusMessage.textContent = error.message || "Unable to process recipe.";
        saveButton.textContent = previewedRecipe ? "Save Recipe" : "Preview Recipe";
    } finally {
        saveButton.disabled = false;
    }
});
