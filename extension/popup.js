const saveButton = document.getElementById("saveButton");
const closeButton = document.getElementById("closeButton");
const statusMessage = document.getElementById("statusMessage");
const previewBox = document.getElementById("previewBox");
const previewTitle = document.getElementById("previewTitle");
const previewIngredients = document.getElementById("previewIngredients");
const previewInstructions = document.getElementById("previewInstructions");
const previewMeta = document.getElementById("previewMeta");

let previewedRecipe = null;

closeButton.addEventListener("click", () => {
    window.close();
});

function renderPreview(recipe) {
    previewBox.hidden = false;
    previewTitle.textContent = recipe?.title || "Untitled recipe";
    previewIngredients.innerHTML = "";
    previewInstructions.innerHTML = "";

    const ingredients = recipe?.ingredients || [];
    if (ingredients.length > 0) {
        ingredients.forEach((ingredient) => {
            const item = document.createElement("li");
            const name = ingredient?.name || "Unknown ingredient";
            item.textContent = name;
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

saveButton.addEventListener("click", async () => {
    saveButton.disabled = true;
    saveButton.textContent = "Working...";
    statusMessage.textContent = "Parsing recipe...";

    try {
        const [tab] = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

        if (!tab?.id) {
            throw new Error("No active tab found.");
        }

        const action = previewedRecipe ? "saveRecipe" : "previewRecipe";
        const response = await chrome.tabs.sendMessage(tab.id, { action });

        if (response?.recipe) {
            if (!previewedRecipe) {
                previewedRecipe = response.recipe;
                renderPreview(previewedRecipe);
                saveButton.textContent = "Save Recipe";
                statusMessage.textContent = "Preview ready. Click save to store it.";
            } else {
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