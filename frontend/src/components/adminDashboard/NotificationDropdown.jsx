import { useEffect, useState } from "react";
import { FaBell } from "react-icons/fa";
import { getNotifications, markNotificationRead } from "../../services/notificationService";

function NotificationDropdown() {
    const [notifications, setNotifications] = useState([]);
    useEffect(() => { getNotifications(false).then(setNotifications).catch(() => setNotifications([])); }, []);

    async function read(id) {
        await markNotificationRead(id);
        setNotifications((items) => items.map((item) => item.id === id ? { ...item, is_read: true } : item));
    }

    return (
        <div className="card shadow border-0" style={{ width: "360px", position: "absolute", top: "65px", right: "0", zIndex: 1000 }}>
            <div className="card-header bg-primary text-white"><strong><FaBell className="me-2" />Notifications</strong></div>
            <div className="card-body p-0" style={{ maxHeight: 420, overflowY: "auto" }}>
                {notifications.length === 0 && <div className="p-3 text-muted">No notifications.</div>}
                {notifications.map((item) => <div key={item.id} className="p-3 border-bottom"><div className="fw-semibold">{item.title}</div><div className="small">{item.message}</div><div className="mt-2 d-flex justify-content-between align-items-center"><small className="text-muted">{new Date(item.created_at).toLocaleString()}</small>{!item.is_read && <button className="btn btn-sm btn-outline-success" onClick={() => read(item.id)}>Mark read</button>}</div></div>)}
            </div>
        </div>
    );
}
export default NotificationDropdown;
