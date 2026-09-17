
import { useEffect, useState } from "react";
import { getProfile } from "../services/employeeProfileService";

function EmployeeTopNavbar() {

    const [profile, setProfile] = useState({});

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

    return (

        <nav
            className="navbar navbar-expand-lg bg-white shadow-sm rounded mb-4 px-4"
            style={{
                minHeight: "75px"
            }}
        >

            <div className="container-fluid">

                <h4
                    className="fw-bold text-primary mb-0"
                >
                    Employee Portal
                </h4>

                <div className="d-flex align-items-center ms-auto">

                    <img
                        src={
                            profile.profile_photo
                                ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${profile.profile_photo}`
                                : "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                        }
                        alt="Profile"
                        style={{
                            width: "45px",
                            height: "45px",
                            borderRadius: "50%",
                            objectFit: "cover",
                            border: "2px solid #2563EB"
                        }}
                    />

                </div>

            </div>

        </nav>

    );

}

export default EmployeeTopNavbar;