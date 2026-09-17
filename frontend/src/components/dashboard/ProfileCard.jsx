function ProfileCard({ employee }) {

    return (

        <div className="card border-0 shadow h-100">

            <div className="card-header bg-success text-white">

                Employee Profile

            </div>

            <div className="card-body text-center">

                <img
                    src={
                        employee.profile_photo
                            ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${employee.profile_photo}`
                            : "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    }
                    alt="Profile"
                    style={{
                        width: "120px",
                        height: "120px",
                        borderRadius: "50%",
                        objectFit: "cover",
                        border: "4px solid #198754"
                    }}
                />

                <h4 className="mt-3">

                    {employee.full_name}

                </h4>

                <p className="text-muted">

                    {employee.designation}

                </p>

                <hr />

                <p>

                    <strong>Department</strong>

                </p>

                <p>

                    {employee.department}

                </p>

            </div>

        </div>

    );

}

export default ProfileCard;