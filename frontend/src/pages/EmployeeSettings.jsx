import { useState } from "react";
import EmployeeLayout from "../components/EmployeeLayout";
import { changePassword } from "../services/changePasswordService";

function EmployeeSettings() {

    const [form, setForm] = useState({
        old_password: "",
        new_password: "",
        confirm_password: ""
    });

    function handleChange(e) {

        setForm({

            ...form,

            [e.target.name]: e.target.value

        });

    }

    async function handleSubmit(e) {

        e.preventDefault();

        if (form.new_password !== form.confirm_password) {

            alert("New Password and Confirm Password do not match.");

            return;

        }

        try {

            const response = await changePassword({
                current_password: form.old_password,
                new_password: form.new_password
            });

            alert(response.message);

            setForm({

                old_password: "",
                new_password: "",
                confirm_password: ""

            });

        }

        catch (error) {

            alert("Unable to change password.");

        }

    }

    return (

        <EmployeeLayout>

            <h2 className="mb-4">

                Settings

            </h2>

            <hr />

            <div className="card shadow border-0">

                <div className="card-header bg-primary text-white">

                    🔐 Change Password

                </div>

                <div className="card-body">

                    <form onSubmit={handleSubmit}>

                        <div className="mb-3">

                            <label>

                                Current Password

                            </label>

                            <input

                                type="password"

                                name="old_password"

                                className="form-control"

                                value={form.old_password}

                                onChange={handleChange}

                                required

                            />

                        </div>

                        <div className="mb-3">

                            <label>

                                New Password

                            </label>

                            <input

                                type="password"

                                name="new_password"

                                className="form-control"

                                value={form.new_password}

                                onChange={handleChange}

                                required

                            />

                        </div>

                        <div className="mb-3">

                            <label>

                                Confirm Password

                            </label>

                            <input

                                type="password"

                                name="confirm_password"

                                className="form-control"

                                value={form.confirm_password}

                                onChange={handleChange}

                                required

                            />

                        </div>

                        <button

                            type="submit"

                            className="btn btn-primary"

                        >

                            Update Password

                        </button>

                    </form>

                </div>

            </div>

            

            

        </EmployeeLayout>

    );

}

export default EmployeeSettings;