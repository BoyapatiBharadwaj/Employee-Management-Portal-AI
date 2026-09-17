import { useEffect, useState } from "react";
import EmployeeLayout from "../components/EmployeeLayout";
import { getMyMonthlyPerformance, getMySuperior } from "../services/hierarchyPerformanceService";

function EmployeeMonthlyPerformance() {
    const [superior, setSuperior] = useState(null);
    const [records, setRecords] = useState([]);

    useEffect(() => {
        Promise.all([getMySuperior(), getMyMonthlyPerformance()]).then(([superiorData, recordData]) => {
            setSuperior(superiorData); setRecords(recordData || []);
        }).catch((error) => alert(error?.response?.data?.detail || "Unable to load performance information."));
    }, []);

    return <EmployeeLayout>
        <div className="mb-4">
            <h2 className="fw-bold">My Monthly Performance</h2>
            <p className="text-muted">Your current reporting relationship and historical monthly results.</p>
        </div>
        <div className="card border-0 shadow-sm mb-4"><div className="card-body">
            <h5 className="mb-3">Current Superior</h5>
            {superior?.superior_name ? <div><strong>{superior.superior_name}</strong><div className="text-muted">{superior.superior_email}</div></div> : <span className="text-muted">No Superior assigned.</span>}
        </div></div>
        <div className="card border-0 shadow-sm"><div className="table-responsive"><table className="table align-middle mb-0"><thead><tr><th>Month</th><th>Superior Rating</th><th>Attendance</th><th>Leave</th><th>Overall</th><th>Rank</th><th>Status</th><th>Feedback</th></tr></thead><tbody>{records.map((record) => <tr key={record.id}><td>{String(record.performance_month).slice(0,7)}</td><td>{record.superior_rating ?? "—"}</td><td>{record.attendance_score ?? "—"}</td><td>{record.leave_score ?? "—"}</td><td className="fw-bold">{record.overall_score ?? "—"}</td><td>{record.rank ?? "—"}</td><td><span className={`badge ${record.status === "Finalized" ? "bg-success" : "bg-warning text-dark"}`}>{record.status}</span></td><td style={{ minWidth: 240 }}>{record.feedback || "—"}</td></tr>)}</tbody></table></div>{records.length === 0 && <div className="p-5 text-center text-muted">No monthly performance records available yet.</div>}</div>
    </EmployeeLayout>;
}

export default EmployeeMonthlyPerformance;
