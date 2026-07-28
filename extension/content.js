chrome.runtime.onMessage.addListener((message) => {

    if (message.action !== "saveRecipe")
        return;

    fetch("http://localhost:8000/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            url: window.location.href,
            html: document.documentElement.outerHTML
        })
    });

});