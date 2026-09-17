import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import EmployeeLayout from "../components/EmployeeLayout";
import { changePassword } from "../services/changePasswordService";
import { getProfile } from "../services/profileService";

function ChangePassword() {

    const navigate = useNavigate();

    const [profile, setProfile] = useState({});

    const [form, setForm] = useState({
        current_password: "",
        new_password: "",
        confirm_password: ""
    });

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

    async function handleSubmit(e) {

        e.preventDefault();

        if (form.new_password !== form.confirm_password) {
            alert("New passwords do not match.");
            return;
        }

        try {

            const response = await changePassword({
                current_password: form.current_password,
                new_password: form.new_password
            });

            if (response.message === "Password changed successfully") {

                alert(response.message);

                localStorage.clear();
                sessionStorage.clear();

                navigate("/", { replace: true });

                window.location.reload();

                return;
            }

            alert(response.message);

        }
        catch (error) {

            console.error(error);

            alert(
                error.response?.data?.message ||
                error.response?.data?.detail ||
                "Unable to change password."
            );

        }

    }

    return (

        <EmployeeLayout>

            {/* Profile Card */}

            <div className="card shadow mb-4">

                <div className="card-body text-center">

                    <img
    src={
        profile.profile_photo
            ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${profile.profile_photo}`
            : "/images/admin.png"
    }
    alt="Profile"
    className="rounded-circle shadow"
    onError={(e) => {
        e.target.src = "/images/admin.png";
    }}
    style={{
        width: "150px",
        height: "150px",
        objectFit: "cover",
        border: "4px solid #0d6efd"
    }}
/>
                    <h2 className="fw-bold mt-3">
                        {profile.username}
                    </h2>

                    <h5 className="text-muted">
                        {profile.designation || profile.role}
                    </h5>

                </div>

            </div>

            {/* Change Password */}

            <div className="card shadow">

                <div className="card-header bg-primary text-white">

                    <h4 className="mb-0">
                        Change Password
                    </h4>

                </div>

                <div className="card-body">

                    <form onSubmit={handleSubmit}>

                        <div className="mb-3">

                            <label className="form-label">
                                Current Password
                            </label>

                            <input
                                type="password"
                                className="form-control"
                                value={form.current_password}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        current_password: e.target.value
                                    })
                                }
                                required
                            />

                        </div>

                        <div className="mb-3">

                            <label className="form-label">
                                New Password
                            </label>

                            <input
                                type="password"
                                className="form-control"
                                value={form.new_password}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        new_password: e.target.value
                                    })
                                }
                                required
                            />

                        </div>

                        <div className="mb-3">

                            <label className="form-label">
                                Confirm Password
                            </label>

                            <input
                                type="password"
                                className="form-control"
                                value={form.confirm_password}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        confirm_password: e.target.value
                                    })
                                }
                                required
                            />

                        </div>

                        <button
                            type="submit"
                            className="btn btn-success"
                        >
                            Change Password
                        </button>

                    </form>

                </div>

            </div>

        </EmployeeLayout>

    );

}

export default ChangePassword;