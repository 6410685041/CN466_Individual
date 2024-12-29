

async function request_page(accessToken) {
    try {
        const response = await fetch(`/liff/check?access_token=${encodeURIComponent(accessToken)}`);
        
        if (response.redirected) {
            // If the server sends a redirect, follow it
            window.location.href = response.url;
        } else if (response.ok) {
            console.log("Page loaded successfully:", await response.json());
        } else {
            console.error("Failed to load the page:", response.status);
        }
    } catch (err) {
        console.error("Error requesting page:", err);
    }
}