import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    FaEnvelope,
    FaLock,
    FaEye,
    FaEyeSlash
} from "react-icons/fa";

import api from "../services/api";

function Login() {

    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    async function handleLogin() {

    try {

        const formData = new URLSearchParams();

        formData.append("username", email);
        formData.append("password", password);

        const response = await api.post(
            "/login",
            formData,
            {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            }
        );

        localStorage.clear();
        sessionStorage.clear();

        localStorage.setItem(
            "access_token",
            response.data.access_token || ""
        );

        localStorage.setItem(
            "role",
            response.data.role || ""
        );

        localStorage.setItem(
            "employee_id",
            String(response.data.employee_id || "")
        );

        localStorage.setItem(
            "user",
            JSON.stringify(response.data.user || {})
        );

        if (response.data.role === "Admin") {
            navigate("/dashboard");
        } else if (["Superior", "CEO"].includes(response.data.role)) {
            navigate("/manager/performance");
        } else {
            navigate("/employee/dashboard");
        }

    } catch (error) {

    alert("Login Failed");
}
}

    return (

        <div
            className="container-fluid"
            style={{
                minHeight: "100vh",
                background:
                    "linear-gradient(135deg,#2563eb,#0f172a)"
            }}
        >

            <div className="row min-vh-100">

                {/* Left Section */}

                <div
                    className="col-lg-7 d-none d-lg-flex align-items-center justify-content-center text-white"
                >

                    <div>

                        <h1
                            className="display-2 fw-bold"
                        >
                            AI Employee
                            <br />
                            Management Portal
                        </h1>

                        <h3 className="mt-4">

                            Modern Human Resource
                            Management Platform

                        </h3>

                        <p
                            className="mt-4 fs-4"
                            style={{
                                maxWidth: "650px",
                                lineHeight: "1.7"
                            }}
                        >

                            Manage employees,
                            attendance,
                            payroll,
                            departments,
                            leave requests,
                            onboarding,
                            offboarding,
                            documents,
                            performance evaluation,
                            and AI-powered analytics
                            from one secure platform.

                        </p>

                    </div>

                </div>

                {/* Login Card */}

                <div
                    className="col-lg-5 d-flex justify-content-center align-items-center"
                >

                    <div
                        className="card border-0 shadow-lg p-5"
                        style={{
                            width: "450px",
                            borderRadius: "20px"
                        }}
                    >

                        <div className="text-center mb-4">

                            <div
                                className="mx-auto mb-3 d-flex justify-content-center align-items-center"
                                style={{
                                    width: "85px",
                                    height: "85px",
                                    borderRadius: "18px",
                                    background:
                                        "linear-gradient(135deg,#2563eb,#1e3a8a)",
                                    color: "#fff",
                                    fontSize: "34px",
                                    fontWeight: "bold"
                                }}
                            >

                                EMP

                            </div>

                            <h2 className="fw-bold">

                                Sign In

                            </h2>

                            <p className="text-muted">

                                Sign in to access your account

                            </p>

                        </div>

                        {/* Email */}

                        <div className="mb-3">

                            <label className="form-label">

                                Email Address

                            </label>

                            <div className="input-group">

                                <span className="input-group-text">

                                    <FaEnvelope />

                                </span>

                                <input
                                    type="email"
                                    className="form-control"
                                    placeholder="Enter your email"
                                    value={email}
                                    onChange={(e) =>
                                        setEmail(e.target.value)
                                    }
                                />

                            </div>

                        </div>

                        {/* Password */}

                        <div className="mb-2">

                            <label className="form-label">

                                Password

                            </label>

                            <div className="input-group">

                                <span className="input-group-text">

                                    <FaLock />

                                </span>

                                <input
                                    type={
                                        showPassword
                                            ? "text"
                                            : "password"
                                    }
                                    className="form-control"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) =>
                                        setPassword(e.target.value)
                                    }
                                />

                                <button
                                    className="btn btn-outline-secondary"
                                    type="button"
                                    onClick={() =>
                                        setShowPassword(!showPassword)
                                    }
                                >

                                    {
                                        showPassword
                                            ? <FaEyeSlash />
                                            : <FaEye />
                                    }

                                </button>

                            </div>

                        </div>

                        <div className="text-end mb-4">

                            <a
                                href="#"
                                className="text-decoration-none"
                            >

                                Forgot Password?

                            </a>

                        </div>

                        <button
                            className="btn btn-primary w-100 py-2 fw-semibold"
                            onClick={handleLogin}
                        >

                            Sign In

                        </button>

                        <hr className="my-4" />

                        <p
                            className="text-center text-muted mb-0"
                            style={{
                                fontSize: "14px"
                            }}
                        >

                            © 2026 AI Employee Management Portal
                            <br />
                            Secure Human Resource Management System

                        </p>

                    </div>

                </div>

            </div>

        </div>

    );

}

export default Login;