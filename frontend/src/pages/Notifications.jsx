import Layout from "../components/Layout";
import NotificationCard from "../components/notifications/NotificationCard";

function Notifications() {
    return <Layout><div className="mb-4"><h2 className="fw-bold">Notification Center</h2><p className="text-muted">Performance reminders and other system notifications.</p></div><NotificationCard /></Layout>;
}
export default Notifications;
