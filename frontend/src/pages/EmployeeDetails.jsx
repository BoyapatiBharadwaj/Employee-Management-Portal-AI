import { useEffect, useState } from "react";
import EmployeeLayout from "../components/EmployeeLayout";
import { getEmployeeDetails } from "../services/employeeDetailsService";

function EmployeeDetails() {

    const [employee, setEmployee] = useState(null);

    useEffect(() => {
        loadEmployee();
    }, []);

    async function loadEmployee() {

        try {

            const data = await getEmployeeDetails();

            setEmployee(data);

        } catch (error) {

            console.error(error);

            alert("Unable to load employee details.");

        }

    }

    if (!employee) {

        return (
            <EmployeeLayout>
                <h3>Loading...</h3>
            </EmployeeLayout>
        );

    }

    return (

        <EmployeeLayout>

            <h2>Employee Details</h2>

            <hr />

            <div className="card shadow">

                <div className="card-body">

                    <div className="text-center mb-4">

                        <img
                            src={
                                employee.profile_photo
                                    ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${employee.profile_photo}`
                                    : "https://via.placeholder.com/180"
                            }
                            alt="Profile"
                            className="rounded-circle border border-primary"
                            style={{
                                width: "180px",
                                height: "180px",
                                objectFit: "cover"
                            }}
                        />

                        <h3 className="mt-3">
                            {employee.full_name}
                        </h3>

                        <h5 className="text-muted">
                            {employee.designation}
                        </h5>

                    </div>

                    <div className="row">

                        <div className="col-md-6">

                            <table className="table table-bordered">

                                <tbody>

                                    <tr>
                                        <th>Employee ID</th>
                                        <td>{employee.employee_id}</td>
                                    </tr>

                                    <tr>
                                        <th>Email</th>
                                        <td>{employee.email}</td>
                                    </tr>

                                    <tr>
                                        <th>Phone</th>
                                        <td>{employee.phone}</td>
                                    </tr>

                                    <tr>
                                        <th>Department</th>
                                        <td>{employee.department}</td>
                                    </tr>

                                    <tr>
                                        <th>Designation</th>
                                        <td>{employee.designation}</td>
                                    </tr>

                                    <tr>
                                        <th>Salary</th>
                                        <td>₹ {employee.salary}</td>
                                    </tr>

                                </tbody>

                            </table>

                        </div>

                        <div className="col-md-6">

                            <table className="table table-bordered">

                                <tbody>

                                    <tr>
                                        <th>Joining Date</th>
                                        <td>{employee.joining_date}</td>
                                    </tr>

                                    <tr>
                                        <th>Date of Birth</th>
                                        <td>{employee.date_of_birth}</td>
                                    </tr>

                                    <tr>
                                        <th>Nationality</th>
                                        <td>{employee.nationality}</td>
                                    </tr>

                                    <tr>
                                        <th>Emergency Contact</th>
                                        <td>{employee.emergency_contact}</td>
                                    </tr>

                                    <tr>
                                        <th>Address</th>
                                        <td>{employee.address}</td>
                                    </tr>

                                </tbody>

                            </table>

                        </div>

                    </div>

                </div>

            </div>

        </EmployeeLayout>

    );

}

export default EmployeeDetails;