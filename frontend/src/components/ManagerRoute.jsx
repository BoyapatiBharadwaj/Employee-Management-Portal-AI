import { Navigate } from "react-router-dom";

function ManagerRoute({ children }) {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");

    if (!token) return <Navigate to="/login" replace />;

    if (!["Superior", "CEO", "Admin"].includes(role)) {
        return <Navigate to="/employee/dashboard" replace />;
    }

    return children;
}

export default ManagerRoute;
