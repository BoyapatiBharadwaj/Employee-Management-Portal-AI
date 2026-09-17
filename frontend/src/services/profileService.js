import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function authHeader() {

    return {

        headers: {

            Authorization: `Bearer ${localStorage.getItem("access_token")}`

        }

    };

}

export async function getProfile() {

    const response = await axios.get(

        `${API}/profile`,

        authHeader()

    );

    return response.data;

}

export async function updateProfile(profile) {

    const response = await axios.put(

        `${API}/profile`,

        profile,

        authHeader()

    );

    return response.data;

}
export async function uploadProfilePhoto(file) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await axios.post(

        `${API}/profile/upload-photo`,

        formData,

        {

            headers: {

                Authorization: `Bearer ${localStorage.getItem("access_token")}`,

                "Content-Type": "multipart/form-data"

            }

        }

    );

    return response.data;

}