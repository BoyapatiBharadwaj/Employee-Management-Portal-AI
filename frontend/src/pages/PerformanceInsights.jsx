import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { getPerformanceInsights, finalizeMonthlyPerformance } from "../services/hierarchyPerformanceService";
import { getDepartments } from "../services/departmentService";

function PerformanceInsights() {
    const [rows, setRows] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [month, setMonth] = useState("");
    const [departmentId, setDepartmentId] = useState("");
    const [loading, setLoading] = useState(true);

    async function load() {
        setLoading(true);
        try {
            const data = await getPerformanceInsights({
                ...(month ? { performance_month: `${month}-01` } : {}),
                ...(departmentId ? { department_id: departmentId } : {}),
            });
            setRows(data || []);
        } catch (error) {
            alert(error?.response?.data?.detail || "Unable to load Performance Insights.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        load();
        getDepartments().then(setDepartments).catch(() => setDepartments([]));
    }, []);

    async function finalize() {
        if (!month) return alert("Select a performance month first.");
        try {
            await finalizeMonthlyPerformance(`${month}-01`);
            alert("Monthly performance records finalized/pending reviews created.");
            load();
        } catch (error) {
            alert(error?.response?.data?.detail || "Unable to finalize the month.");
        }
    }

    return (
        <Layout>
            <div className="d-flex justify-content-between align-items-start mb-4 gap-3">
                <div>
                    <h2 className="fw-bold mb-1">Performance Insights</h2>
                    <p className="text-muted">Previous-month organization-wide performance, rankings and pending reviews.</p>
                </div>
                <button className="btn btn-outline-primary" onClick={finalize}>Finalize Selected Month</button>
            </div>

            <div className="card shadow-sm border-0 mb-4">
                <div className="card-body">
                    <div className="row g-3">
                        <div className="col-md-4"><label className="form-label">Performance Month</label><input type="month" className="form-control" value={month} onChange={(e) => setMonth(e.target.value)} /></div>
                        <div className="col-md-4"><label className="form-label">Department</label><select className="form-select" value={departmentId} onChange={(e) => setDepartmentId(e.target.value)}><option value="">All Departments</option>{departments.map((d) => <option key={d.id} value={d.id}>{d.department_name}</option>)}</select></div>
                        <div className="col-md-4 d-flex align-items-end"><button className="btn btn-primary w-100" onClick={load}>Apply Filters</button></div>
                    </div>
                </div>
            </div>

            <div className="row g-3 mb-4">
                <div className="col-md-3"><div className="card border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Records</div><div className="fs-3 fw-bold">{rows.length}</div></div></div></div>
                <div className="col-md-3"><div className="card border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Finalized</div><div className="fs-3 fw-bold text-success">{rows.filter((r) => r.status === "Finalized").length}</div></div></div></div>
                <div className="col-md-3"><div className="card border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Pending Review</div><div className="fs-3 fw-bold text-warning">{rows.filter((r) => r.status === "Pending Review").length}</div></div></div></div>
                <div className="col-md-3"><div className="card border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Average Score</div><div className="fs-3 fw-bold">{rows.filter(r => r.overall_score != null).length ? (rows.filter(r => r.overall_score != null).reduce((s, r) => s + Number(r.overall_score), 0) / rows.filter(r => r.overall_score != null).length).toFixed(2) : "—"}</div></div></div></div>
            </div>

            <div className="card shadow-sm border-0">
                <div className="table-responsive">
                    <table className="table table-hover align-middle mb-0">
                        <thead><tr><th>Rank</th><th>Employee</th><th>Department</th><th>Superior</th><th>Rating</th><th>Attendance</th><th>Leave</th><th>Overall</th><th>Status</th><th>Feedback</th></tr></thead>
                        <tbody>
                        {!loading && rows.map((row) => (
                            <tr key={row.id}>
                                <td><span className="badge bg-dark">{row.rank ?? "—"}</span></td>
                                <td><strong>{row.employee_name}</strong></td>
                                <td>{row.department || "—"}</td>
                                <td>{row.superior_name || "—"}</td>
                                <td>{row.superior_rating ?? "—"}</td>
                                <td>{row.attendance_score ?? "—"}</td>
                                <td>{row.leave_score ?? "—"}</td>
                                <td className="fw-bold">{row.overall_score ?? "—"}</td>
                                <td><span className={`badge ${row.status === "Finalized" ? "bg-success" : row.status === "Pending Review" ? "bg-warning text-dark" : "bg-info"}`}>{row.status}</span></td>
                                <td style={{ minWidth: 220 }}>{row.feedback || "—"}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
                {rows.length === 0 && <div className="text-center text-muted p-5">No Performance Insights found for the selected month.</div>}
            </div>
        </Layout>
    );
}

export default PerformanceInsights;
