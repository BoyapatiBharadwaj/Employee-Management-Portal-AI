import { useEffect, useMemo, useState } from "react";
import Layout from "../components/Layout";
import { getPerformanceInsights, finalizeMonthlyPerformance, correctFinalizedPerformance } from "../services/hierarchyPerformanceService";
import { getDepartments } from "../services/departmentService";
import { getEmployees } from "../services/employeeService";

function PerformanceInsights() {
    const [rows, setRows] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [month, setMonth] = useState("");
    const [departmentId, setDepartmentId] = useState("");
    const [superiorId, setSuperiorId] = useState("");
    const [employeeId, setEmployeeId] = useState("");
    const [rank, setRank] = useState("");
    const [scope, setScope] = useState("overall");
    const [sortBy, setSortBy] = useState("rank");
    const [sortOrder, setSortOrder] = useState("asc");
    const [loading, setLoading] = useState(true);
    const [correction, setCorrection] = useState(null);

    const superiors = useMemo(() => employees.filter((e) => ["Superior", "CEO"].includes(e.user_role)), [employees]);

    async function load() {
        if (scope === "department" && !departmentId) return alert("Select a department for department ranking.");
        if (scope === "superior" && !superiorId) return alert("Select a Superior for team ranking.");
        setLoading(true);
        try {
            const data = await getPerformanceInsights({
                ...(month ? { performance_month: `${month}-01` } : {}),
                ...(departmentId ? { department_id: departmentId } : {}),
                ...(superiorId ? { superior_id: superiorId } : {}),
                ...(employeeId ? { employee_id: employeeId } : {}),
                ...(rank ? { rank } : {}),
                ranking_scope: scope,
                sort_by: sortBy,
                sort_order: sortOrder,
            });
            setRows(data || []);
        } catch (error) { alert(error?.response?.data?.detail || "Unable to load Performance Insights."); }
        finally { setLoading(false); }
    }

    useEffect(() => {
        Promise.all([getDepartments(), getEmployees()]).then(([d, e]) => { setDepartments(d || []); setEmployees(e || []); }).catch(() => {});
        load();
    }, []);

    async function finalize() {
        if (!month) return alert("Select a performance month first.");
        try { await finalizeMonthlyPerformance(`${month}-01`); alert("Monthly performance processed."); await load(); }
        catch (error) { alert(error?.response?.data?.detail || "Unable to finalize the month."); }
    }

    async function saveCorrection(event) {
        event.preventDefault();
        try {
            await correctFinalizedPerformance(correction.id, Number(correction.rating), correction.feedback, correction.reason);
            setCorrection(null); await load(); alert("Controlled correction saved and audited.");
        } catch (error) { alert(error?.response?.data?.detail || "Unable to save correction."); }
    }

    return <Layout>
        <div className="d-flex justify-content-between align-items-start mb-4 gap-3"><div><h2 className="fw-bold mb-1">Performance Insights</h2><p className="text-muted">Previous-month HR/Admin performance reporting with scoped rankings, filtering and sorting.</p></div><button className="btn btn-outline-primary" onClick={finalize}>Finalize Selected Month</button></div>
        <div className="card shadow-sm border-0 mb-4"><div className="card-body"><div className="row g-3">
            <div className="col-md-3"><label className="form-label">Performance Month</label><input type="month" className="form-control" value={month} onChange={(e) => setMonth(e.target.value)} /></div>
            <div className="col-md-3"><label className="form-label">Ranking View</label><select className="form-select" value={scope} onChange={(e) => { setScope(e.target.value); setRank(""); }}>{<><option value="overall">Overall Organization</option><option value="department">Department Ranking</option><option value="superior">Superior / Team Ranking</option></>}</select></div>
            <div className="col-md-3"><label className="form-label">Department</label><select className="form-select" value={departmentId} onChange={(e) => setDepartmentId(e.target.value)}><option value="">All Departments</option>{departments.map((d) => <option key={d.id} value={d.id}>{d.department_name}</option>)}</select></div>
            <div className="col-md-3"><label className="form-label">Superior</label><select className="form-select" value={superiorId} onChange={(e) => setSuperiorId(e.target.value)}><option value="">All Superiors</option>{superiors.map((e) => <option key={e.id} value={e.id}>{e.full_name}</option>)}</select></div>
            <div className="col-md-3"><label className="form-label">Employee</label><select className="form-select" value={employeeId} onChange={(e) => setEmployeeId(e.target.value)}><option value="">All Employees</option>{employees.map((e) => <option key={e.id} value={e.id}>{e.full_name}</option>)}</select></div>
            <div className="col-md-3"><label className="form-label">Rank</label><input type="number" min="1" className="form-control" value={rank} onChange={(e) => setRank(e.target.value)} placeholder="Any rank" /></div>
            <div className="col-md-3"><label className="form-label">Sort By</label><select className="form-select" value={sortBy} onChange={(e) => setSortBy(e.target.value)}><option value="rank">Rank</option><option value="overall_score">Overall Score</option><option value="employee_name">Employee</option><option value="department">Department</option><option value="superior_name">Superior</option></select></div>
            <div className="col-md-3"><label className="form-label">Order</label><select className="form-select" value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}><option value="asc">Ascending</option><option value="desc">Descending</option></select></div>
            <div className="col-12"><button className="btn btn-primary" onClick={load}>Apply Filters & Ranking</button></div>
        </div></div></div>
        <div className="row g-3 mb-4"><div className="col-md-3"><div className="card border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Records</div><div className="fs-3 fw-bold">{rows.length}</div></div></div></div><div className="col-md-3"><div className="card border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Finalized</div><div className="fs-3 fw-bold text-success">{rows.filter(r => r.status === "Finalized").length}</div></div></div></div><div className="col-md-3"><div className="card border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Pending Review</div><div className="fs-3 fw-bold text-warning">{rows.filter(r => r.status === "Pending Review").length}</div></div></div></div><div className="col-md-3"><div className="card border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Average Score</div><div className="fs-3 fw-bold">{rows.filter(r => r.overall_score != null).length ? (rows.filter(r => r.overall_score != null).reduce((s, r) => s + Number(r.overall_score), 0) / rows.filter(r => r.overall_score != null).length).toFixed(2) : "—"}</div></div></div></div></div>
        <div className="card shadow-sm border-0"><div className="table-responsive"><table className="table table-hover align-middle mb-0"><thead><tr><th>Rank</th><th>Employee</th><th>Department</th><th>Superior</th><th>Rating</th><th>Attendance</th><th>Leave</th><th>Overall</th><th>Status</th><th></th></tr></thead><tbody>{!loading && rows.map((row) => <tr key={row.id}><td><span className="badge bg-dark">{row.rank ?? "—"}</span></td><td><strong>{row.employee_name}</strong><div className="small text-muted">{row.performance_month?.slice(0,7)}</div></td><td>{row.department || "—"}</td><td>{row.superior_name || "—"}</td><td>{row.superior_rating ?? "—"}</td><td>{row.attendance_score ?? "—"}</td><td>{row.leave_score ?? "—"}</td><td className="fw-bold">{row.overall_score ?? "—"}</td><td><span className={`badge ${row.status === "Finalized" ? "bg-success" : row.status === "Pending Review" ? "bg-warning text-dark" : "bg-info"}`}>{row.status}</span></td><td>{row.status === "Finalized" ? <button className="btn btn-sm btn-outline-warning" onClick={() => setCorrection({ id: row.id, rating: row.superior_rating, feedback: row.feedback || "", reason: "" })}>Correct</button> : ""}</td></tr>)}</tbody></table></div>{rows.length === 0 && <div className="text-center text-muted p-5">No Performance Insights found.</div>}</div>
        {correction && <div className="modal d-block" tabIndex="-1" style={{ background: "rgba(0,0,0,.45)" }}><div className="modal-dialog"><div className="modal-content"><form onSubmit={saveCorrection}><div className="modal-header"><h5 className="modal-title">Controlled Admin Correction</h5><button type="button" className="btn-close" onClick={() => setCorrection(null)} /></div><div className="modal-body"><div className="alert alert-warning">Only finalized records can be corrected. The reason and before/after values are written to the audit history.</div><label className="form-label">Rating</label><input type="number" min="1" max="100" className="form-control mb-3" value={correction.rating} onChange={(e) => setCorrection({ ...correction, rating: e.target.value })} required /><label className="form-label">Feedback</label><textarea className="form-control mb-3" rows="4" value={correction.feedback} onChange={(e) => setCorrection({ ...correction, feedback: e.target.value })} required /><label className="form-label">Correction Reason</label><textarea className="form-control" rows="4" value={correction.reason} onChange={(e) => setCorrection({ ...correction, reason: e.target.value })} required /></div><div className="modal-footer"><button type="button" className="btn btn-secondary" onClick={() => setCorrection(null)}>Cancel</button><button className="btn btn-warning">Save Correction</button></div></form></div></div></div>}
    </Layout>;
}
export default PerformanceInsights;
