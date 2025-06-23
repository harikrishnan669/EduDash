import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [file, setFile] = useState(null);
    const [uploaded, setUploaded] = useState(false);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        const formData = new FormData();
        formData.append('excel', file);

        try {
            await axios.post('http://localhost:5000/upload', formData);
            setUploaded(true);
        } catch (err) {
            console.error('Upload failed:', err);
        }
    };
    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-8">
            <div className="bg-white shadow-xl rounded-2xl p-10 w-full max-w-xl">
                <h1 className="text-xl font-bold mb-6 text-blue-700 text-center align-center">
                    KTU Student Mark Analyzer
                </h1>

                <input
                    type="file"
                    accept=".xlsx"
                    onChange={handleFileChange}
                    className="mb-4 w-full text-sm text-gray-700 border border-gray-300 cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />

                <button
                    onClick={handleUpload}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg py-2 px-6 transition-all duration-200"
                >
                    Upload & Analyze
                </button>
            </div>

            {uploaded && (
                <div className="mt-10 w-full max-w-6xl">
                    <h2 className="text-2xl font-semibold text-center mb-4 text-gray-800">
                        Student Performance Dashboard
                    </h2>
                    <div className="rounded-xl overflow-hidden shadow-lg border-2 border-gray-300">
                        <iframe title="TEST" width="1140" height="541.25"
                                src="https://app.powerbi.com/reportEmbed?reportId=8c06e3eb-1497-4f4e-8967-431512199602&autoAuth=true&ctid=c265993b-3650-4240-945e-3cf6562de766"
                                frameBorder="0" allowFullScreen="true"></iframe>
                    </div>
                </div>
            )}
        </div>
    );
}
export default App;
