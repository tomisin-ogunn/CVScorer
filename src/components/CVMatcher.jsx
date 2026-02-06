import React, { useState } from 'react';

const CVMatcher = () => {
  const [cvText, setCvText] = useState('');
  const [jobDescText, setJobDescText] = useState('');
  const [similarityScore, setSimilarityScore] = useState('');
  const [cvFileName, setCvFileName] = useState('');
  const [jobFileName, setJobFileName] = useState('');

  const handleClearCV = () => {
    setCvText('');
    setCvFileName('');
  };

  const handleClearJob = () => {
    setJobDescText('');
    setJobFileName('');
  };

  const handleCVUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setCvFileName(file.name);
      setCvText(`File uploaded: ${file.name}`);
    }
  };

  const handleJobUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setJobFileName(file.name);
      setJobDescText(`File uploaded: ${file.name}`);
    }
  };

  const handleCheck = () => {
    // Placeholder function - returns static similarity score
    setSimilarityScore('85%');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-blue-600 text-white px-6 py-4 shadow-lg fixed top-0 w-full z-10">
        <h1 className="text-2xl font-bold">CV Matcher</h1>
      </nav>

      {/* Main Content */}
      <div className="pt-20 px-6 pb-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left and Middle Columns - Input Boxes */}
            <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* CV Input Box */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">CV Input</h2>
                <textarea
                  className="w-full h-96 p-4 border-2 border-gray-300 rounded-lg resize-none focus:outline-none focus:border-blue-500 transition-colors"
                  placeholder="Input CV Data"
                  value={cvText}
                  onChange={(e) => setCvText(e.target.value)}
                />
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={handleClearCV}
                    className="flex-1 bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                  >
                    Clear
                  </button>
                  <label className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors text-center cursor-pointer">
                    Upload PDF
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleCVUpload}
                      className="hidden"
                    />
                  </label>
                </div>
                {cvFileName && (
                  <p className="mt-2 text-sm text-gray-600">Selected: {cvFileName}</p>
                )}
              </div>

              {/* Job Description Input Box */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Job Description Input</h2>
                <textarea
                  className="w-full h-96 p-4 border-2 border-gray-300 rounded-lg resize-none focus:outline-none focus:border-blue-500 transition-colors"
                  placeholder="Input Job Description"
                  value={jobDescText}
                  onChange={(e) => setJobDescText(e.target.value)}
                />
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={handleClearJob}
                    className="flex-1 bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                  >
                    Clear
                  </button>
                  <label className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors text-center cursor-pointer">
                    Upload PDF
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleJobUpload}
                      className="hidden"
                    />
                  </label>
                </div>
                {jobFileName && (
                  <p className="mt-2 text-sm text-gray-600">Selected: {jobFileName}</p>
                )}
              </div>
            </div>

            {/* Right Column - Similarity Score Box */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Similarity Score</h2>
                <div className="border-2 border-gray-300 rounded-lg p-8 bg-gray-50 min-h-[200px] flex items-center justify-center">
                  {similarityScore ? (
                    <div className="text-center">
                      <p className="text-6xl font-bold text-blue-600">{similarityScore}</p>
                      <p className="text-gray-600 mt-2">Match Score</p>
                    </div>
                  ) : (
                    <p className="text-gray-400 text-center">Score will appear here after clicking Check</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Check Button */}
          <div className="mt-8 flex justify-center">
            <button
              onClick={handleCheck}
              className="bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-12 rounded-lg text-xl shadow-lg transition-colors"
            >
              Check Similarity
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CVMatcher;
