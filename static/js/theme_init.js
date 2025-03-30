/**
 * Theme initialization script
 * This runs before Streamlit fully initializes to prevent flicker
 */

(function() {
    // Immediately set dark theme
    document.body.classList.add('dark-theme');
    
    function applyDarkTheme() {
        const stApp = document.querySelector('.stApp');
        if (stApp) {
            stApp.setAttribute('data-theme', 'dark');
        }
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.setAttribute('data-theme', 'dark');
        }
    }

    // Apply when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        applyDarkTheme();
        const observer = new MutationObserver(m => applyDarkTheme());
        observer.observe(document.body, { childList: true, subtree: true });
    });
})();
