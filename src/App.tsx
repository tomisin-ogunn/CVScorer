import React, { useState } from 'react';
import Navbar from './components/Navbar';
import InputBox from './components/InputBox';
import SimilarityScore from './components/SimilarityScore';

const App: React.FC = () => {
  const [cvText, setCvText] = useState<string>('');
  const [jobDescText, setJobDescText] = useState<string>('');
  const [similarityScore, setSimilarityScore] = useState<number | null>(null);

  const handleClearCV = () => {
    setCvText('');
  };

  const handleClearJobDesc = () => {
    setJobDescText('');
  };

  const handleCheck = () => {
    // Placeholder function: generates a random score between 40 and 99
    // In a real implementation, this would call a backend API
    const randomScore = Math.floor(Math.random() * 60) + 40;
    setSimilarityScore(randomScore);
  };

  const isCheckDisabled = cvText.trim() === '' || jobDescText.trim() === '';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navbar />
      
      <main className="pt-20 pb-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Desktop and Mobile Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* CV Input */}
            <div className="lg:col-span-1">
              <InputBox
                title="CV Input"
                placeholder="Input CV Data"
                value={cvText}
                onChange={setCvText}
                onClear={handleClearCV}
              />
            </div>

            {/* Job Description Input */}
            <div className="lg:col-span-1">
              <InputBox
                title="Job Description"
                placeholder="Input Job Description"
                value={jobDescText}
                onChange={setJobDescText}
                onClear={handleClearJobDesc}
              />
            </div>

            {/* Similarity Score */}
            <div className="lg:col-span-1">
              <SimilarityScore score={similarityScore} />
            </div>
          </div>

          {/* Check Button */}
          <div className="flex justify-center mt-8">
            <button
              onClick={handleCheck}
              disabled={isCheckDisabled}
              className={`px-12 py-4 text-lg font-semibold rounded-lg shadow-lg transition-all duration-200 ${
                isCheckDisabled
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white hover:shadow-xl transform hover:-translate-y-0.5'
              } focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2`}
              aria-label="Check similarity"
            >
              {isCheckDisabled ? 'Enter Both Inputs' : 'Check Similarity'}
            </button>
          </div>

          {/* Info Message */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500">
              This is a front-end prototype. The similarity score is a placeholder value.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
