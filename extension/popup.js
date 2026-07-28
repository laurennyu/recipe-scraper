const saveButton = document.getElementById("saveButton");
const closeButton = document.getElementById("closeButton");

closeButton.addEventListener("click", () => {
    window.close();
});

saveButton.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    chrome.tabs.sendMessage(
        tab.id,
        {
            action: "saveRecipe"
        }
    );
});