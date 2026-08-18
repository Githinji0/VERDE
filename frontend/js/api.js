/* Centralized REST API client for VERDE */

const API_BASE = "";

async function apiRequest(endpoint, options = {}) {
    const defaultHeaders = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    };

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || data.detail || `HTTP Error ${response.status}`);
        }
        return data;
    } catch (err) {
        console.error(`API Error on ${endpoint}:`, err);
        throw err;
    }
}

export const api = {
    // Generic HTTP helpers
    get: (endpoint) => apiRequest(endpoint, { method: "GET" }),
    post: (endpoint, body) => apiRequest(endpoint, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
    put: (endpoint, body) => apiRequest(endpoint, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
    delete: (endpoint) => apiRequest(endpoint, { method: "DELETE" }),

    // BRAIN
    getBrainHealth: () => apiRequest("/api/brain/health"),
    testBrainAuth: (creds) => apiRequest("/api/brain/auth/test", { method: "POST", body: JSON.stringify(creds) }),
    connectBrain: (creds) => apiRequest("/api/brain/connect", { method: "POST", body: JSON.stringify(creds) }),
    disconnectBrain: () => apiRequest("/api/brain/disconnect", { method: "POST" }),

    // Candidates
    getCandidates: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/api/candidates?${query}`);
    },
    getCandidateDetail: (id) => apiRequest(`/api/candidates/${id}`),
    generateCandidates: (body) => apiRequest("/api/candidates/generate", { method: "POST", body: JSON.stringify(body) }),
    validateCandidate: (id) => apiRequest(`/api/candidates/${id}/validate`, { method: "POST" }),
    simulateCandidate: (id, settings) => apiRequest(`/api/candidates/${id}/simulate`, { method: "POST", body: JSON.stringify(settings) }),
    mutateCandidate: (id) => apiRequest(`/api/candidates/${id}/mutate`, { method: "POST" }),

    // Simulations
    getSimulations: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/api/simulations?${query}`);
    },
    getSimulationDetail: (id) => apiRequest(`/api/simulations/${id}`),
    pollSimulation: (id) => apiRequest(`/api/simulations/${id}/poll`, { method: "POST" }),

    // Analytics
    getOverviewAnalytics: () => apiRequest("/api/analytics/overview"),
    getParetoData: () => apiRequest("/api/analytics/pareto"),
    getFamilyStats: () => apiRequest("/api/analytics/families"),
    getFieldStats: () => apiRequest("/api/analytics/fields"),
    getOperatorStats: () => apiRequest("/api/analytics/operators"),

    // Research
    getFamilies: () => apiRequest("/api/research/families"),
    getFamilyDetail: (code) => apiRequest(`/api/research/families/${code}`),
    getFields: () => apiRequest("/api/research/fields"),
    getOperators: () => apiRequest("/api/research/operators"),
    getResearchMemory: () => apiRequest("/api/research/memory"),
    getLineage: (id) => apiRequest(`/api/research/lineage/${id}`),

    // AI Lab
    getAIProviders: () => apiRequest("/api/ai/providers"),
    validateAIKey: (provider, key) => apiRequest("/api/ai/validate-key", { method: "POST", body: JSON.stringify({ provider_name: provider, api_key: key }) }),
    generateAIHypothesis: (provider, family) => apiRequest("/api/ai/hypothesis", { method: "POST", body: JSON.stringify({ provider_name: provider, family_code: family }) }),

    // Settings
    getSettings: () => apiRequest("/api/settings"),
    updateSettings: (data) => apiRequest("/api/settings", { method: "PUT", body: JSON.stringify(data) }),

    // Logs
    getLogs: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/api/logs?${query}`);
    },
    getLogDetail: (id) => apiRequest(`/api/logs/${id}`)
};
