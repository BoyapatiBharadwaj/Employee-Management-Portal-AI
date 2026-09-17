import { useEffect, useState } from "react";
import EmployeeLayout from "../components/EmployeeLayout";
import { getMyTeam, getTeamMonthlyPerformance, evaluateMonthly } from "../services/hierarchyPerformanceService";

function ManagerPerformance() {
    const [team, setTeam] = useState([]);
    const [records, setRecords] = useState([]);
    const [selected, setSelected] = useState(null);
    const [rating, setRating] = useState("");
    const [feedback, setFeedback] = useState("");
    const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));

    async function load() {
        try {
            const [teamData, recordData] = await Promise.all([getMyTeam(), getTeamMonthlyPerformance()]);
            setTeam(teamData || []);
            setRecords(recordData || []);
        } catch (error) {
            alert(error?.response?.data?.detail || "Unable to load your team.");
        }
    }

    useEffect(() => { load(); }, []);

    async function submit(event) {
        event.preventDefault();
        if (!selected) return;
        try {
            await evaluateMonthly({
                employee_id: selected.id,
                performance_month: `${month}-01`,
                rating: Number(rating),
                feedback,
            });
            alert("Monthly evaluation submitted.");
            setSelected(null); setRating(""); setFeedback("");
            load();
        } catch (error) {
            alert(error?.response?.data?.detail || "Unable to submit evaluation.");
        }
    }

    return (
        <EmployeeLayout>
            <div className="mb-4">
                <h2 className="fw-bold">My Team & Monthly Performance</h2>
                <p className="text-muted">Evaluate only employees who currently report directly to you.</p>
            </div>
            <div className="row g-4">
                <div className="col-lg-7">
                    <div className="card border-0 shadow-sm">
                        <div className="card-header bg-dark text-white">Employees Under Me</div>
                        <div className="table-responsive">
                            <table className="table align-middle mb-0">
                                <thead><tr><th>Employee</th><th>Department</th><th>Designation</th><th>Action</th></tr></thead>
                                <tbody>{team.map((employee) => {
                                    const record = records.find(r => r.employee_id === employee.id && String(r.performance_month).startsWith(month));
                                    return <tr key={employee.id}><td><strong>{employee.full_name}</strong><div className="small text-muted">{employee.employee_id}</div></td><td>{employee.department || "—"}</td><td>{employee.designation}</td><td><button className="btn btn-sm btn-primary" onClick={() => { setSelected(employee); setRating(record?.superior_rating || ""); setFeedback(record?.feedback || ""); }}>Evaluate</button></td></tr>;
                                })}</tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div className="col-lg-5">
                    <div className="card border-0 shadow-sm">
                        <div className="card-header bg-primary text-white">Monthly Evaluation</div>
                        <div className="card-body">
                            {!selected ? <p className="text-muted">Select a direct report to submit the monthly evaluation.</p> : <form onSubmit={submit}>
                                <div className="mb-3"><label className="form-label">Employee</label><input className="form-control" value={selected.full_name} disabled /></div>
                                <div className="mb-3"><label className="form-label">Performance Month</label><input type="month" className="form-control" value={month} onChange={(e) => setMonth(e.target.value)} required /></div>
                                <div className="mb-3"><label className="form-label">Superior Rating (1–100)</label><input type="number" className="form-control" min="1" max="100" value={rating} onChange={(e) => setRating(e.target.value)} required /></div>
                                <div className="mb-3"><label className="form-label">Feedback</label><textarea className="form-control" rows="5" value={feedback} onChange={(e) => setFeedback(e.target.value)} required /></div>
                                <button className="btn btn-primary w-100">Submit Evaluation</button>
                            </form>}
                        </div>
                    </div>
                </div>
            </div>
        </EmployeeLayout>
    );
}

export default ManagerPerformance;
