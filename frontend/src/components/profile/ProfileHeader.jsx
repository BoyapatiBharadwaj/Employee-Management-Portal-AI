function ProfileHeader({ profile, onPhotoChange, uploading }) {

    return (

        <div
            className="card border-0 shadow mb-4"
            style={{
                borderRadius: "20px"
            }}
        >

            <div className="card-body text-center">

                <img
                    src={
                        profile.profile_photo
                            ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${profile.profile_photo}?v=${Date.now()}`
                            : "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    }
                    alt="Profile"
                    style={{
                        width: "170px",
                        height: "170px",
                        borderRadius: "50%",
                        objectFit: "cover",
                        border: "5px solid #2563EB"
                    }}
                />

                <div className="mt-3">

                    <label
                        className="btn btn-primary"
                        style={{
                            cursor: uploading ? "not-allowed" : "pointer"
                        }}
                    >

                        {uploading ? "Uploading..." : "Change Photo"}

                        <input
                            type="file"
                            accept="image/*"
                            onChange={onPhotoChange}
                            disabled={uploading}
                            style={{ display: "none" }}
                        />

                    </label>

                </div>

                <h3 className="mt-3">

                    {profile.full_name}

                </h3>

                <h5 className="text-muted">

                    {profile.designation}

                </h5>

                <span
                    className="badge bg-primary"
                >

                    {profile.employee_id}

                </span>

            </div>

        </div>

    );

}

export default ProfileHeader;