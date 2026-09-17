import api from "./api";

export async function getMySuperior() {
    const response = await api.get("/hierarchy/my-superior");
    return response.data;
}

export async function getMyTeam() {
    const response = await api.get("/hierarchy/team");
    return response.data;
}

export async function assignSuperior(employeeId, payload) {
    const response = await api.post(`/hierarchy/${employeeId}/superior`, payload);
    return response.data;
}

export async function getHierarchyHistory(employeeId) {
    const response = await api.get(`/hierarchy/history/${employeeId}`);
    return response.data;
}

export async function evaluateMonthly(payload) {
    const response = await api.post("/performance/monthly/evaluate", payload);
    return response.data;
}

export async function getMyMonthlyPerformance() {
    const response = await api.get("/performance/monthly/me");
    return response.data;
}

export async function getTeamMonthlyPerformance() {
    const response = await api.get("/performance/monthly/team");
    return response.data;
}

export async function getPerformanceInsights(params = {}) {
    const response = await api.get("/performance/insights", { params });
    return response.data;
}

export async function finalizeMonthlyPerformance(performanceMonth) {
    const response = await api.post("/performance/monthly/finalize", null, {
        params: { performance_month: performanceMonth },
    });
    return response.data;
}

export async function getAuditLogs() {
    const response = await api.get("/audit-logs");
    return response.data;
}
