chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!message || !message.action) {
        return;
    }

    const endpoint = message.action === "previewRecipe" ? "/preview" : message.action === "saveRecipe" ? "/save" : null;

    if (!endpoint) {
        return;
    }

    fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            url: window.location.href,
            html: document.documentElement.outerHTML
        })
    })
        .then((response) => response.json())
        .then((data) => sendResponse({ ok: true, recipe: data }))
        .catch((error) => sendResponse({ ok: false, error: error.message }));

    return true;
});