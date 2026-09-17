import api from "./api";

export async function getNotifications(unreadOnly = false) {
    const response = await api.get("/notifications/me", { params: { unread_only: unreadOnly } });
    return response.data;
}

export async function markNotificationRead(id) {
    const response = await api.put(`/notifications/${id}/read`);
    return response.data;
}

export async function markAllNotificationsRead() {
    const response = await api.put("/notifications/read-all");
    return response.data;
}
