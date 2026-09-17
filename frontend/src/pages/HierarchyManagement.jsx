import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { getEmployees } from "../services/employeeService";
import {
    assignSuperior,
    getHierarchyHistory,
} from "../services/hierarchyPerformanceService";

function HierarchyManagement() {
    const [employees, setEmployees] = useState([]);
    const [selected, setSelected] = useState(null);
    const [superiorId, setSuperiorId] = useState("");
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    async function loadEmployees() {
        setLoading(true);
        try {
            const data = await getEmployees();
            setEmployees(data || []);
        } catch (error) {
            alert(error?.response?.data?.detail || "Unable to load employees.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { loadEmployees(); }, []);

    async function chooseEmployee(employee) {
        setSelected(employee);
        setSuperiorId(employee.superior_id ?? "");
        try {
            const data = await getHierarchyHistory(employee.id);
            setHistory(data || []);
        } catch {
            setHistory([]);
        }
    }

    async function saveAssignment(event) {
        event.preventDefault();
        if (!selected) return;
        try {
            await assignSuperior(selected.id, {
                superior_id: superiorId ? Number(superiorId) : null,
                effective_from: new Date().toLocaleDateString("en-CA"),
            });
            alert("Reporting relationship updated.");
            await loadEmployees();
            const refreshed = employees.find((item) => item.id === selected.id);
            if (refreshed) await chooseEmployee({ ...refreshed, superior_id: superiorId || null });
        } catch (error) {
            alert(error?.response?.data?.detail || "Unable to update reporting relationship.");
        }
    }

    return (
        <Layout>
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 className="fw-bold mb-1">Employee Hierarchy</h2>
                    <p className="text-muted mb-0">Assign one active Superior while preserving reporting history.</p>
                </div>
            </div>

            <div className="row g-4">
                <div className="col-lg-7">
                    <div className="card shadow-sm border-0">
                        <div className="card-header bg-dark text-white">Employees</div>
                        <div className="table-responsive">
                            <table className="table table-hover align-middle mb-0">
                                <thead><tr><th>Employee</th><th>Department</th><th>Designation</th><th>Superior</th></tr></thead>
                                <tbody>
                                {!loading && employees.map((employee) => (
                                    <tr key={employee.id} onClick={() => chooseEmployee(employee)} style={{ cursor: "pointer" }}>
                                        <td><strong>{employee.full_name}</strong><div className="small text-muted">{employee.employee_id}</div></td>
                                        <td>{employee.department?.department_name || employee.department_name || "—"}</td>
                                        <td>{employee.designation}</td>
                                        <td>{employee.superior_name || employee.superior?.full_name || "Not assigned"}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div className="col-lg-5">
                    <div className="card shadow-sm border-0 mb-4">
                        <div className="card-header bg-primary text-white">Change Superior</div>
                        <div className="card-body">
                            {!selected ? <p className="text-muted mb-0">Select an employee from the table.</p> : (
                                <form onSubmit={saveAssignment}>
                                    <div className="mb-3">
                                        <label className="form-label">Employee</label>
                                        <input className="form-control" value={selected.full_name} disabled />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Active Superior</label>
                                        <select className="form-select" value={superiorId} onChange={(e) => setSuperiorId(e.target.value)}>
                                            <option value="">No Superior / Top Level</option>
                                            {employees.filter((item) => item.id !== selected.id && ["Superior", "CEO"].includes(item.user_role)).map((item) => (
                                                <option key={item.id} value={item.id}>{item.full_name} — {item.user_role}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <button className="btn btn-primary w-100">Save Reporting Relationship</button>
                                </form>
                            )}
                        </div>
                    </div>

                    <div className="card shadow-sm border-0">
                        <div className="card-header">Historical Assignments</div>
                        <div className="card-body p-0">
                            {history.length === 0 ? <p className="text-muted p-3 mb-0">No history available.</p> : (
                                <div className="list-group list-group-flush">
                                    {history.map((item) => (
                                        <div className="list-group-item" key={item.id}>
                                            <div className="fw-semibold">{item.superior_name || "No Superior"}</div>
                                            <div className="small text-muted">{item.effective_from} → {item.effective_to || "Present"}</div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
}

export default HierarchyManagement;
