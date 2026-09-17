import { useEffect, useState } from "react";
import EmployeeLayout from "../components/EmployeeLayout";
import { getTeamMonthlyPerformance, evaluateMonthly } from "../services/hierarchyPerformanceService";
import { getNotifications, markNotificationRead } from "../services/notificationService";

function ManagerPerformance() {
    const [team, setTeam] = useState([]);
    const [selected, setSelected] = useState(null);
    const [rating, setRating] = useState("");
    const [feedback, setFeedback] = useState("");
    const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
    const [loading, setLoading] = useState(true);
    const [notifications, setNotifications] = useState([]);

    async function load() {
        setLoading(true);
        try {
            const [teamData, notificationData] = await Promise.all([getTeamMonthlyPerformance(`${month}-01`), getNotifications(true)]);
            setTeam(teamData || []);
            setNotifications(notificationData || []);
        } catch (error) {
            alert(error?.response?.data?.detail || "Unable to load your team.");
            setTeam([]); setNotifications([]);
        } finally { setLoading(false); }
    }

    useEffect(() => { load(); }, [month]);

    function choose(employee) {
        setSelected(employee);
        setRating(employee.superior_rating ?? "");
    }

    async function submit(event) {
        event.preventDefault();
        if (!selected) return;
        try {
            await evaluateMonthly({ employee_id: selected.id, performance_month: `${month}-01`, rating: Number(rating), feedback });
            alert("Monthly evaluation submitted.");
            setSelected(null); setRating(""); setFeedback(""); await load();
        } catch (error) {
            alert(error?.response?.data?.detail || "Unable to submit evaluation.");
        }
    }

    return <EmployeeLayout>
        <div className="mb-4"><h2 className="fw-bold">My Team & Monthly Performance</h2><p className="text-muted">Only direct reports currently assigned to you are shown.</p></div>
        <div className="card border-0 shadow-sm mb-4"><div className="card-body"><div className="row g-3 align-items-end"><div className="col-md-4"><label className="form-label">Performance Month</label><input type="month" className="form-control" value={month} onChange={(e) => setMonth(e.target.value)} /></div><div className="col-md-8"><div className="alert alert-light mb-0">Evaluation window: <strong>25th through month end</strong>. Finalized records are read-only.</div></div></div></div></div>
        <div className="card border-0 shadow-sm mb-4"><div className="card-header bg-warning-subtle">Pending Review Notifications</div><div className="card-body">{notifications.length === 0 ? <span className="text-muted">No unread performance notifications.</span> : notifications.map((item) => <div key={item.id} className="d-flex justify-content-between align-items-start border-bottom py-2"><div><strong>{item.title}</strong><div className="small text-muted">{item.message}</div></div><button className="btn btn-sm btn-outline-success" onClick={async () => { await markNotificationRead(item.id); setNotifications((items) => items.filter((n) => n.id !== item.id)); }}>Read</button></div>)}</div></div>
        <div className="row g-4">
            <div className="col-lg-8"><div className="card border-0 shadow-sm"><div className="card-header bg-dark text-white">Employees Under Me</div><div className="table-responsive"><table className="table align-middle mb-0"><thead><tr><th>Employee</th><th>Department</th><th>Status</th><th>Rating</th><th>Attendance</th><th>Leave</th><th>Overall</th><th>Rank</th><th></th></tr></thead><tbody>{!loading && team.map((employee) => <tr key={employee.id}><td><strong>{employee.full_name}</strong><div className="small text-muted">{employee.employee_id}</div></td><td>{employee.department || "—"}</td><td><span className={`badge ${employee.evaluation_status === "Finalized" ? "bg-success" : employee.evaluation_status === "Pending Review" ? "bg-warning text-dark" : "bg-info"}`}>{employee.evaluation_status}</span></td><td>{employee.superior_rating ?? "—"}</td><td>{employee.attendance_score ?? "—"}</td><td>{employee.leave_score ?? "—"}</td><td>{employee.overall_score ?? "—"}</td><td>{employee.rank ?? "—"}</td><td>{employee.evaluation_status === "Finalized" ? <button className="btn btn-sm btn-outline-secondary" disabled>Finalized</button> : <button className="btn btn-sm btn-primary" onClick={() => choose(employee)}>Evaluate</button>}</td></tr>)}</tbody></table></div>{!loading && team.length === 0 && <div className="p-5 text-center text-muted">No direct reports found.</div>}</div></div>
            <div className="col-lg-4"><div className="card border-0 shadow-sm"><div className="card-header bg-primary text-white">Monthly Evaluation</div><div className="card-body">{!selected ? <p className="text-muted mb-0">Select a direct report.</p> : <form onSubmit={submit}><div className="mb-3"><label className="form-label">Employee</label><input className="form-control" value={selected.full_name} disabled /></div><div className="mb-3"><label className="form-label">Superior Rating (1–100)</label><input type="number" className="form-control" min="1" max="100" value={rating} onChange={(e) => setRating(e.target.value)} required /></div><div className="mb-3"><label className="form-label">Feedback</label><textarea className="form-control" rows="6" value={feedback} onChange={(e) => setFeedback(e.target.value)} required /></div><button className="btn btn-primary w-100">Submit Evaluation</button></form>}</div></div></div>
        </div>
    </EmployeeLayout>;
}
export default ManagerPerformance;
