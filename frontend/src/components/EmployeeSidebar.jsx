import { Link, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { getProfile } from "../services/employeeProfileService";

function EmployeeSidebar() {

    const navigate = useNavigate();
    const location = useLocation();

    const [profile, setProfile] = useState({});
    const role = localStorage.getItem("role");

    useEffect(() => {
        loadProfile();
    }, []);

    async function loadProfile() {

        try {

            const data = await getProfile();
            setProfile(data);

        } catch (error) {

            console.log(error);

        }

    }

    const handleLogout = () => {

        if (!window.confirm("Are you sure you want to logout?")) {
            return;
        }

        localStorage.clear();

        navigate("/", { replace: true });

    };

    const isActive = (path) => location.pathname === path;

    return (

        <div
            className="bg-dark text-white d-flex flex-column"
            style={{
                width: "270px",
                minHeight: "100vh"
            }}
        >

            {/* Employee Card */}

            <div className="text-center p-4 border-bottom">

                <img
                    src={
                        profile.profile_photo
                            ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${profile.profile_photo}`
                            : "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    }
                    alt="Profile"
                    style={{
                        width: "110px",
                        height: "110px",
                        borderRadius: "50%",
                        objectFit: "cover",
                        border: "4px solid white"
                    }}
                />

                <h4 className="mt-3 mb-1">

                    {profile.full_name || "Employee"}

                </h4>

                <small className="text-secondary">

                    {profile.designation || ""}

                </small>

            </div>

            {/* Navigation */}

            <ul className="nav flex-column p-3 flex-grow-1">

                <li className="nav-item mb-2">
                    <Link
                        to="/employee/dashboard"
                        className={`nav-link ${
                            isActive("/employee/dashboard")
                                ? "bg-primary text-white rounded"
                                : "text-white"
                        }`}
                    >
                        Dashboard
                    </Link>
                </li>

                <li className="nav-item mb-2">
                    <Link
                        to="/employee/profile"
                        className={`nav-link ${
                            isActive("/employee/profile")
                                ? "bg-primary text-white rounded"
                                : "text-white"
                        }`}
                    >
                        My Profile
                    </Link>
                </li>

                <li className="nav-item mb-2">
                    <Link
                        to="/employee/details"
                        className={`nav-link ${
                            isActive("/employee/details")
                                ? "bg-primary text-white rounded"
                                : "text-white"
                        }`}
                    >
                        Employee Details
                    </Link>
                </li>

                <li className="nav-item mb-2">
                    <Link
                        to="/employee/attendance"
                        className={`nav-link ${
                            isActive("/employee/attendance")
                                ? "bg-primary text-white rounded"
                                : "text-white"
                        }`}
                    >
                        Attendance
                    </Link>
                </li>

                <li className="nav-item mb-2">
                    <Link
                        to="/employee/performance"
                        className={`nav-link ${
                            isActive("/employee/performance")
                                ? "bg-primary text-white rounded"
                                : "text-white"
                        }`}
                    >
                        My Performance
                    </Link>
                </li>

                <li className="nav-item mb-2">
                    <Link
                        to="/employee/monthly-performance"
                        className={`nav-link ${
                            isActive("/employee/monthly-performance")
                                ? "bg-primary text-white rounded"
                                : "text-white"
                        }`}
                    >
                        Monthly Performance
                    </Link>
                </li>

                {["Superior", "CEO", "Admin"].includes(role) && (
                <li className="nav-item mb-2">
                    <Link
                        to="/manager/performance"
                        className={`nav-link ${
                            isActive("/manager/performance")
                                ? "bg-primary text-white rounded"
                                : "text-white"
                        }`}
                    >
                        My Team / Evaluations
                    </Link>
                </li>

                )}

                <li className="nav-item mb-2">
                    <Link
                        to="/employee/leave"
                        className={`nav-link ${
                            isActive("/employee/leave")
                                ? "bg-primary text-white rounded"
                                : "text-white"
                        }`}
                    >
                        Leave
                    </Link>
                </li>

               <li className="nav-item mb-2">
    <Link
        to="/employee/payroll"
        className={`nav-link ${
            isActive("/employee/payroll")
                ? "bg-primary text-white rounded"
                : "text-white"
        }`}
    >
        Payroll
    </Link>
</li>

<li className="nav-item mb-2">
    <Link
        to="/employee/ai"
        className={`nav-link ${
            isActive("/employee/ai")
                ? "bg-primary text-white rounded"
                : "text-white"
        }`}
    >
        🤖 AI Assistant
    </Link>
</li>

<li className="nav-item mb-2">
    <Link
        to="/employee/settings"
        className={`nav-link ${
            isActive("/employee/settings")
                ? "bg-primary text-white rounded"
                : "text-white"
        }`}
    >
        Settings
    </Link>
</li>

            </ul>

            <div className="p-3">

                <button
                    className="btn btn-danger w-100"
                    onClick={handleLogout}
                >
                    Logout
                </button>

            </div>

        </div>

    );

}

export default EmployeeSidebar;