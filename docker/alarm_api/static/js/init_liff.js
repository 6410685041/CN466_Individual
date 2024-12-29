async function initializeLiff(liffId) {
    try {
        await liff.init({ liffId: liffId }); // Wait for LIFF initialization

        if (!liff.isLoggedIn()) {
            liff.login(); // Redirect to login
        } else {
            try {
                const profile = await liff.getProfile(); // Await profile fetch
                console.log("Profile:", profile);

                // Update the UI
                document.getElementById("profile-picture").src = profile.pictureUrl;
                document.getElementById("display-name").innerText = profile.displayName;
                
                const accessToken = liff.getAccessToken();
                if (accessToken) {
                    try {
                        await request_page(accessToken);
                    } catch (err) {
                        console.error("Error requesting page:", err);
                    }
                } else {
                    console.error('No access token available.');
                }
            } catch (err) {
                console.error("Error fetching profile:", err);
            }
        }
    } catch (err) {
        console.error('LIFF Initialization failed', err);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    if (typeof config !== 'undefined' && config.liffId) {
        initializeLiff(config.liffId); // Call the async function
    } else {
        console.error('LIFF ID is not properly configured in the HTML template.');
    }
});

// async function request_page(accessToken) {
//     try {
//         const response = await fetch(`/liff/check?access_token=${encodeURIComponent(accessToken)}`);
        
//         if (response.redirected) {
//             // If the server sends a redirect, follow it
//             window.location.href = response.url;
//         } else if (response.ok) {
//             console.log("Page loaded successfully:", await response.json());
//         } else {
//             console.error("Failed to load the page:", response.status);
//         }
//     } catch (err) {
//         console.error("Error requesting page:", err);
//     }
// }
