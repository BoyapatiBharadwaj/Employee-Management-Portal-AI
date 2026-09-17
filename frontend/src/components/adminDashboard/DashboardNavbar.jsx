import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    FaBars,
    FaSearch,
    FaBell,
    FaUser,
    FaCog,
    FaKey,
    FaSignOutAlt,
    FaChevronDown
} from "react-icons/fa";

import NotificationDropdown from "./NotificationDropdown";
import { getProfile } from "../../services/profileService";

function DashboardNavbar() {

    const navigate = useNavigate();

    const [profile, setProfile] = useState({});
    const [showNotifications, setShowNotifications] = useState(false);
    const [showProfileMenu, setShowProfileMenu] = useState(false);

    useEffect(() => {

        loadProfile();

    }, []);

    async function loadProfile() {

        try {

            const data = await getProfile();

            setProfile(data);

        }

        catch (error) {

            console.log(error);

        }

    }

    function logout() {

        localStorage.removeItem("access_token");
        localStorage.removeItem("user_email");

        navigate("/");

    }

    const today = new Date().toLocaleDateString(
        "en-IN",
        {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }
    );

    return (

        <nav
            className="bg-white rounded-4 shadow-sm px-4 py-3 mb-4 d-flex justify-content-between align-items-center position-relative"
        >

            {/* Left */}

            <div className="d-flex align-items-center">

                <FaBars
                    className="fs-3 text-primary me-3"
                    style={{ cursor: "pointer" }}
                />

                <div>

                    <h2 className="fw-bold mb-0">

                        Dashboard

                    </h2>

                    <small className="text-muted">

                        {today}

                    </small>

                </div>

            </div>

            {/* Right */}

            <div className="d-flex align-items-center gap-3">

                {/* Search */}

                <div
                    className="input-group"
                    style={{ width: "320px" }}
                >

                    <span className="input-group-text bg-light">

                        <FaSearch />

                    </span>

                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search employee..."
                    />

                </div>

                {/* Notifications */}

                <div className="position-relative">

                    <button
                        className="btn btn-light rounded-circle"
                        style={{
                            width: "48px",
                            height: "48px"
                        }}
                        onClick={() =>
                            setShowNotifications(!showNotifications)
                        }
                    >

                        <FaBell />

                    </button>

                    <span
                        className="badge bg-danger position-absolute"
                        style={{
                            top: "-5px",
                            right: "-2px"
                        }}
                    >

                        3

                    </span>

                    {

                        showNotifications &&

                        <NotificationDropdown />

                    }

                </div>

                {/* Profile */}

                <div className="position-relative">

                    <div
                        className="d-flex align-items-center bg-white shadow-sm rounded-4 px-3 py-2"
                        style={{
                            cursor: "pointer"
                        }}
                        onClick={() =>
                            setShowProfileMenu(!showProfileMenu)
                        }
                    >

                        <img
                            src={
                                profile.profile_photo
                                    ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${profile.profile_photo}`
                                    : "/images/admin.png"
                            }
                            alt="Admin"
                            width="48"
                            height="48"
                            className="rounded-circle"
                            style={{
                                objectFit: "cover"
                            }}
                        />

                        <div className="ms-3">

                            <strong>

                                {profile.username || "Admin"}

                            </strong>

                            <br />

                            <small className="text-muted">

                                {profile.designation || "HR Manager"}

                            </small>

                        </div>

                        <FaChevronDown className="ms-3" />

                    </div>

                    {

                        showProfileMenu &&

                        <div
                            className="card shadow border-0 position-absolute"
                            style={{
                                width: "220px",
                                right: "0",
                                top: "70px",
                                zIndex: 1000
                            }}
                        >

                            <div className="list-group list-group-flush">

                                <button
                                    className="list-group-item list-group-item-action"
                                    onClick={() => navigate("/profile")}
                                >

                                    <FaUser className="me-2" />

                                    My Profile

                                </button>

                                <button
                                    className="list-group-item list-group-item-action"
                                    onClick={() => navigate("/settings")}
                                >

                                    <FaCog className="me-2" />

                                    Settings

                                </button>

                                <button
                                    className="list-group-item list-group-item-action"
                                    onClick={() => navigate("/change-password")}
                                >

                                    <FaKey className="me-2" />

                                    Change Password

                                </button>

                                <button
                                    className="list-group-item list-group-item-action text-danger"
                                    onClick={logout}
                                >

                                    <FaSignOutAlt className="me-2" />

                                    Logout

                                </button>

                            </div>

                        </div>

                    }

                </div>

            </div>

        </nav>

    );

}

export default DashboardNavbar;