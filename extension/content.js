chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!message || !message.action) {
        return;
    }

    const endpoint = message.action === "previewRecipe" ? "/preview" : message.action === "saveRecipe" ? "/save" : null;

    if (!endpoint) {
        return;
    }

    const body = message.action === "saveRecipe"
        ? message.recipe
        : {
            url: window.location.href,
            html: document.documentElement.outerHTML
        };

    const headers = {
        "Content-Type": "application/json"
    };
    if (message.action === "saveRecipe" && message.username) {
        headers["X-Recipe-Username"] = message.username;
    }

    const requestPath = message.action === "saveRecipe" && message.username
        ? `${endpoint}?username=${encodeURIComponent(message.username)}`
        : endpoint;

    fetch(`https://recipe-scraper-ffis.onrender.com${requestPath}`, {
        method: "POST",
        headers,
        body: JSON.stringify(body)
    })
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail ? JSON.stringify(data.detail) : "Request failed.");
            }
            return data;
        })
        .then((data) => sendResponse({ ok: true, recipe: data }))
        .catch((error) => sendResponse({ ok: false, error: error.message }));

    return true;
});
