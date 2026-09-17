import {
    deleteDocument
} from "../../services/employeeDocumentService";

function DocumentList({

    documents,

    refresh

}) {

    function getBadge(status) {

        switch (status) {

            case "Approved":
                return "success";

            case "Rejected":
                return "danger";

            default:
                return "warning";

        }

    }

    async function handleDelete(id) {

        const confirmDelete = window.confirm(
            "Are you sure you want to delete this document?"
        );

        if (!confirmDelete) {

            return;

        }

        try {

            const response = await deleteDocument(id);

            alert(response.message);

            if (refresh) {

                refresh();

            }

        }

        catch (error) {

            console.log(error);

            alert("Unable to delete document.");

        }

    }

    return (

        <div className="card shadow">

            <div className="card-header bg-success text-white">

                My Documents

            </div>

            <div className="card-body">

                {

                    documents.length === 0 ? (

                        <div className="text-center p-4">

                            <h5>No documents uploaded.</h5>

                        </div>

                    ) : (

                        <table className="table table-hover align-middle">

                            <thead>

                                <tr>

                                    <th>Document</th>

                                    <th>File Name</th>

                                    <th>Status</th>

                                    <th>Uploaded</th>

                                    <th className="text-center">

                                        Action

                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                {

                                    documents.map((doc) => (

                                        <tr key={doc.id}>

                                            <td>

                                                {doc.document_type}

                                            </td>

                                            <td>

                                                {doc.document_name}

                                            </td>

                                            <td>

                                                <span
                                                    className={`badge bg-${getBadge(doc.status)}`}
                                                >

                                                    {doc.status}

                                                </span>

                                            </td>

                                            <td>

                                                {

                                                    new Date(
                                                        doc.uploaded_at
                                                    ).toLocaleDateString()

                                                }

                                            </td>

                                            <td className="text-center">

    <a

        href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${doc.file_path}`}

        target="_blank"

        rel="noopener noreferrer"

        className="btn btn-sm btn-primary me-2"

    >

        View

    </a>

    {

        doc.status === "Pending" && (

            <button

                className="btn btn-sm btn-danger"

                onClick={() => handleDelete(doc.id)}

            >

                Delete

            </button>

        )

    }

</td>

                                        </tr>

                                    ))

                                }

                            </tbody>

                        </table>

                    )

                }

            </div>

        </div>

    );

}

export default DocumentList;