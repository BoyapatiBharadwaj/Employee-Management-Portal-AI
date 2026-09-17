import { useEffect, useState } from "react";
import { FaBell, FaCheck } from "react-icons/fa";
import { getNotifications, markAllNotificationsRead, markNotificationRead } from "../../services/notificationService";

function NotificationCard() {
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);

    async function load() {
        try {
            setLoading(true);
            setNotifications(await getNotifications(false));
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { load(); }, []);

    async function read(id) {
        await markNotificationRead(id);
        await load();
    }

    async function readAll() {
        await markAllNotificationsRead();
        await load();
    }

    const unread = notifications.filter((item) => !item.is_read).length;

    return (
        <div className="card shadow border-0 rounded-4">
            <div className="card-header bg-white d-flex justify-content-between align-items-center">
                <div><h4 className="fw-bold mb-0"><FaBell className="me-2" /> Notifications</h4><small className="text-muted">{unread} unread</small></div>
                <button className="btn btn-sm btn-outline-primary" onClick={readAll} disabled={!unread}><FaCheck className="me-1" /> Mark all read</button>
            </div>
            <div className="card-body p-0">
                {loading && <div className="p-4 text-center text-muted">Loading notifications…</div>}
                {!loading && notifications.length === 0 && <div className="p-4 text-center text-muted">No notifications yet.</div>}
                {!loading && notifications.map((item) => (
                    <div key={item.id} className={`p-3 border-bottom ${item.is_read ? "bg-light" : ""}`}>
                        <div className="d-flex justify-content-between gap-3">
                            <div><div className="fw-semibold">{item.title}</div><div className="small text-muted">{item.message}</div><div className="small text-secondary mt-1">{new Date(item.created_at).toLocaleString()}</div></div>
                            {!item.is_read && <button className="btn btn-sm btn-outline-success" onClick={() => read(item.id)}>Read</button>}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default NotificationCard;
