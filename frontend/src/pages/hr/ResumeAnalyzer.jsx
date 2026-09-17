import React, { useState } from "react";
import api from "../../services/api";

const ResumeAnalyzer = () => {

    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState("");

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const analyzeResume = async () => {

        if (!file) {
            alert("Please select a PDF resume.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {

            setLoading(true);
            setResult("");

            const response = await api.post(
                "/resume/analyze",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );

            setResult(response.data.analysis);

        } catch (error) {

            console.error(error);

            setResult(
                "Failed to analyze resume."
            );

        } finally {

            setLoading(false);

        }

    };

    return (
        <div className="container mt-4">

            <div className="card shadow">

                <div className="card-header bg-primary text-white">

                    <h3>📄 AI Resume Analyzer</h3>

                </div>

                <div className="card-body">

                    <h5>Upload Candidate Resume</h5>

                    <input
                        type="file"
                        className="form-control mt-3"
                        accept=".pdf"
                        onChange={handleFileChange}
                    />

                    <button
                        className="btn btn-primary mt-3"
                        onClick={analyzeResume}
                        disabled={loading}
                    >
                        {loading ? "Analyzing..." : "Analyze Resume"}
                    </button>

                    {result && (

                        <div className="card mt-4">

                            <div className="card-header">
                                AI Analysis
                            </div>

                            <div className="card-body">

                                <pre
                                    style={{
                                        whiteSpace: "pre-wrap",
                                        fontFamily: "inherit"
                                    }}
                                >
                                    {result}
                                </pre>

                            </div>

                        </div>

                    )}

                </div>

            </div>

        </div>
    );

};

export default ResumeAnalyzer;