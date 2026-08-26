import { useEffect, useState } from "react";

import EmployeeLayout from "../components/EmployeeLayout";

import ProfileHeader from "../components/profile/ProfileHeader";
import PersonalTab from "../components/profile/PersonalTab";
import ProfessionalTab from "../components/profile/ProfessionalTab";
import DocumentsTab from "../components/profile/DocumentsTab";

import {
    getProfile,
    updateProfile
} from "../services/employeeProfileService";

import { uploadProfilePhoto } from "../services/profilePhotoService";

function EmployeeProfile() {

    const [profile, setProfile] = useState({});

    const [activeTab, setActiveTab] = useState("personal");

    const [uploading, setUploading] = useState(false);

    useEffect(() => {

        loadProfile();

    }, []);

    async function loadProfile() {

        try {

            const data = await getProfile();

            setProfile(data);

        }

        catch {

            alert("Unable to load profile");

        }

    }

    async function handlePhotoChange(e) {

        const file = e.target.files[0];

        if (!file) return;

        try {

            setUploading(true);

            await uploadProfilePhoto(file);

            alert("Profile photo uploaded successfully.");

            await loadProfile();

        }

        catch (error) {

            console.log(error);

            alert("Profile photo upload failed.");

        }

        finally {

            setUploading(false);

            e.target.value = "";

        }

    }

    function handleChange(e) {

        setProfile({

            ...profile,

            [e.target.name]: e.target.value

        });

    }

    async function handleSubmit() {

        try {

            await updateProfile(profile);

            alert("Profile Updated Successfully");

            loadProfile();

        }

        catch {

            alert("Update Failed");

        }

    }

    return (

        <EmployeeLayout>

            <ProfileHeader

                profile={profile}

                onPhotoChange={handlePhotoChange}

                uploading={uploading}

            />

            <ul className="nav nav-tabs mb-4">

                <li className="nav-item">

                    <button

                        className={`nav-link ${
                            activeTab === "personal"
                                ? "active"
                                : ""
                        }`}

                        onClick={() =>
                            setActiveTab("personal")
                        }

                    >

                        Personal

                    </button>

                </li>

                <li className="nav-item">

                    <button

                        className={`nav-link ${
                            activeTab === "professional"
                                ? "active"
                                : ""
                        }`}

                        onClick={() =>
                            setActiveTab("professional")
                        }

                    >

                        Professional

                    </button>

                </li>

                <li className="nav-item">

                    <button

                        className={`nav-link ${
                            activeTab === "documents"
                                ? "active"
                                : ""
                        }`}

                        onClick={() =>
                            setActiveTab("documents")
                        }

                    >

                        Documents

                    </button>

                </li>

            </ul>

            <div className="card border-0 shadow">

                <div className="card-body">

                    {

                        activeTab === "personal" && (

                            <PersonalTab

                                profile={profile}

                                handleChange={handleChange}

                            />

                        )

                    }

                    {

                        activeTab === "professional" && (

                            <ProfessionalTab

                                profile={profile}

                            />

                        )

                    }

                    {

                        activeTab === "documents" && (

                            <DocumentsTab />

                        )

                    }

                </div>

            </div>

            {

                activeTab !== "documents"

                &&

                <div className="text-end mt-4">

                    <button

                        className="btn btn-primary"

                        onClick={handleSubmit}

                    >

                        Save Changes

                    </button>

                </div>

            }

        </EmployeeLayout>

    );

}

export default EmployeeProfile;