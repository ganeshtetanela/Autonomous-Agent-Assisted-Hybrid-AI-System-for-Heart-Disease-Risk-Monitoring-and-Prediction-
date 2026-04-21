const API_URL = 'http://127.0.0.1:8000';

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    async request(endpoint, method = 'GET', data = null) {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            method,
            headers,
        };

        if (data && method !== 'GET') {
            config.body = JSON.stringify(data);
        } else if (data && method === 'GET') {
            // Transform data to query params if needed
        }

        try {
            const response = await fetch(`${API_URL}${endpoint}`, config);
            const result = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    window.dispatchEvent(new CustomEvent('unauthorized'));
                }
                throw new Error(result.detail || 'API Request Failed');
            }
            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    logout() {
        this.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('role');
    }
}

const api = new ApiClient();
