/**
 * Centralized API Client for standardized fetch handling
 */

const API_BASE = '/api';

/**
 * Enhanced fetch wrapper with success checking and data extraction
 * @param {string} endpoint - API endpoint (relative to /api)
 * @param {Object} options - Fetch options
 * @returns {Promise<any>} - Processed data
 */
export const apiClient = async (endpoint, options = {}) => {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    const timestamp = new Date().toISOString();
    const method = options.method || 'GET';
    const startTime = performance.now();

    const dispatchDebugEvent = (status, errorMsg = null) => {
        const duration = Math.round(performance.now() - startTime);
        const event = new CustomEvent('api-debug-log', {
            detail: {
                url,
                method,
                status,
                error: errorMsg,
                duration
            }
        });
        window.dispatchEvent(event);
    };

    const token = localStorage.getItem('agroguard_token');

    // Proactive Expiration Check
    if (token) {
        try {
            const payloadStr = atob(token.split('.')[1]);
            const payload = JSON.parse(payloadStr);
            if (payload.exp && payload.exp * 1000 < Date.now()) {
                console.warn(`[${timestamp}] API FETCH ABORTED: Token expired client-side`);
                localStorage.removeItem('agroguard_token');
                localStorage.removeItem('agroguard_user');
                window.location.href = '/login';
                throw new Error("Session expired. Please log in again.");
            }
        } catch {
            console.error("Failed to parse JWT payload");
        }
    }

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        // Log response status code
        console.log(`[${timestamp}] API ${method} ${url} - Status: ${response.status}`);

        let json = null;
        try {
            json = await response.json();
            // Log response body
            console.log("API Response:", json);
        } catch {
            console.log("API Response: [Empty or Non-JSON Body]");
        }

        // Handle specific status codes
        if (response.status === 401) {
            dispatchDebugEvent(response.status, "Unauthorized");
            localStorage.removeItem('agroguard_token');
            localStorage.removeItem('agroguard_user');
            window.location.href = '/login';
            throw new Error("Unauthorized");
        }

        if (response.status === 500) {
            dispatchDebugEvent(response.status, "Server error. Check logs.");
            throw new Error("Server error. Check logs.");
        }

        // Check success field and response.ok
        if (!response.ok || (json && json.success === false)) {
            const errorMsg = (json && (json.error || json.message)) || `API Error: ${response.status} ${response.statusText}`;
            dispatchDebugEvent(response.status, errorMsg);
            throw new Error(errorMsg);
        }

        dispatchDebugEvent(response.status, null);

        // Safe data extraction
        const extractedData = json?.data !== undefined ? json.data : (json?.success ? json : json);

        return {
            data: extractedData,
            timestamp,
            status: response.status
        };
    } catch (error) {
        // If network error, show "Server unreachable"
        if (error.name === 'TypeError') {
            const msg = "Server unreachable";
            console.error(`[${new Date().toISOString()}] NETWORK ERROR ${method} ${url}: `, msg);
            dispatchDebugEvent(0, msg);
            throw new Error(msg);
        }

        // Ensure other errors are logged
        console.error(`[${new Date().toISOString()}] FETCH ERROR ${method} ${url}:`, error.message);
        throw error;
    }
};
