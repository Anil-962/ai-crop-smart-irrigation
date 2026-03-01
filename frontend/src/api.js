import { apiClient } from './utils/apiClient';

export const diseaseApi = {
    predict: async (base64Image) => {
        return apiClient('/predict/disease', {
            method: 'POST',
            body: JSON.stringify({ image_base64: base64Image }),
        });
    }
};

export const irrigationApi = {
    getRecommendation: async (data) => {
        return apiClient('/predict/irrigation', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
    control: async (data) => {
        return apiClient('/irrigation/control', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
};

export const healthApi = {
    check: async () => {
        return apiClient('/health');
    },
    getScore: async () => {
        return apiClient('/health/score');
    }
};

export const authApi = {
    login: async (email, password) => {
        return apiClient('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
    },
    signup: async (name, email, password) => {
        return apiClient('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ name, email, password }),
        });
    }
};

export const dashboardApi = {
    getData: async (zoneId = 'all') => {
        const query = zoneId !== 'all' ? `?zone_id=${zoneId}` : '';
        return apiClient(`/dashboard${query}`);
    }
};

export const analyticsApi = {
    getData: async (zoneId = 'all') => {
        const query = zoneId !== 'all' ? `?zone_id=${zoneId}` : '';
        return apiClient(`/analytics${query}`);
    }
};

export const alertsApi = {
    getAlerts: async (zoneId = 'all') => {
        const query = zoneId !== 'all' ? `?zone_id=${zoneId}` : '';
        return apiClient(`/alerts${query}`);
    },
    resolveAlert: async (alertId) => {
        return apiClient(`/alerts/${alertId}/resolve`, {
            method: 'POST'
        });
    }
};

