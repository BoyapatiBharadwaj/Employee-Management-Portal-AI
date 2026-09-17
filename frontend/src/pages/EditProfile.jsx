import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import Layout from "../components/Layout";

import {
    getProfile,
    updateProfile,
    uploadProfilePhoto
} from "../services/profileService";

function EditProfile() {

    const navigate = useNavigate();

    const [form, setForm] = useState({
        username: "",
        phone: "",
        department: "",
        designation: "",
        profile_photo: ""
    });

    const [photo, setPhoto] = useState(null);

    const [preview, setPreview] = useState("");

    useEffect(() => {
        loadProfile();
    }, []);

    async function loadProfile() {

        try {

            const data = await getProfile();

            setForm({

                username: data.username || "",
                phone: data.phone || "",
                department: data.department || "",
                designation: data.designation || "",
                profile_photo: data.profile_photo || ""

            });

            if (data.profile_photo) {

                setPreview(
                    `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${data.profile_photo}`
                );

            } else {

                setPreview("/images/admin.png");

            }

        }

        catch (error) {

            console.log(error);

            alert("Unable to load profile.");

        }

    }

    function handleChange(e) {

        setForm({

            ...form,
            [e.target.name]: e.target.value

        });

    }

    function handlePhotoChange(e) {

        const file = e.target.files[0];

        if (!file) return;

        setPhoto(file);

        setPreview(URL.createObjectURL(file));

    }

    async function handleSubmit(e) {

        e.preventDefault();

        try {

            if (photo) {

                await uploadProfilePhoto(photo);

            }

            await updateProfile(form);

            alert("Profile updated successfully.");

            navigate("/profile");

        }

        catch (error) {

            console.log(error);

            alert("Unable to update profile.");

        }

    }

    return (

        <Layout>

            <div className="container mt-4">

                <div className="card shadow">

                    <div className="card-header bg-primary text-white">

                        <h3>Edit Profile</h3>

                    </div>

                    <div className="card-body">

                        <form onSubmit={handleSubmit}>

                            <div className="text-center mb-4">

                                <img
                                    src={preview}
                                    alt="Profile"
                                    className="rounded-circle shadow mb-3"
                                    style={{
                                        width: "160px",
                                        height: "160px",
                                        objectFit: "cover",
                                        border: "5px solid #0d6efd"
                                    }}
                                />

                                <input
                                    type="file"
                                    className="form-control"
                                    accept="image/*"
                                    onChange={handlePhotoChange}
                                />

                            </div>

                            <div className="mb-3">

                                <label>Username</label>

                                <input
                                    className="form-control"
                                    name="username"
                                    value={form.username}
                                    onChange={handleChange}
                                    required
                                />

                            </div>

                            <div className="mb-3">

                                <label>Phone</label>

                                <input
                                    className="form-control"
                                    name="phone"
                                    value={form.phone}
                                    onChange={handleChange}
                                />

                            </div>

                            <div className="mb-3">

                                <label>Department</label>

                                <input
                                    className="form-control"
                                    name="department"
                                    value={form.department}
                                    onChange={handleChange}
                                />

                            </div>

                            <div className="mb-3">

                                <label>Designation</label>

                                <input
                                    className="form-control"
                                    name="designation"
                                    value={form.designation}
                                    onChange={handleChange}
                                />

                            </div>

                            <button
                                type="submit"
                                className="btn btn-success me-2"
                            >
                                Save Changes
                            </button>

                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={() => navigate("/profile")}
                            >
                                Cancel
                            </button>

                        </form>

                    </div>

                </div>

            </div>

        </Layout>

    );

}

export default EditProfile;