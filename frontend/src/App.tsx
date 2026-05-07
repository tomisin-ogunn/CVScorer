import React, { useState } from 'react';
import Navbar from './components/Navbar';
import InputBox from './components/InputBox';
import SimilarityScore from './components/SimilarityScore';

const App: React.FC = () => {
  const [cvText, setCvText] = useState<string>('');
  const [jobDescText, setJobDescText] = useState<string>('');
  const [apiKey, setApiKey] = useState<string>('');
  const [similarityScore, setSimilarityScore] = useState<number | null>(null);
  const [matchedKeywords, setMatchedKeywords] = useState<string[]>([]);
  const [missingKeywords, setMissingKeywords] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleClearCV = () => {
    setCvText('');
  };

  const handleClearJobDesc = () => {
    setJobDescText('');
  };

  const handleCheck = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cv_text: cvText,
          job_description: jobDescText,
          api_key: apiKey || undefined,
        }),
      });

      if (!response.ok) {
        // Try to parse error message from backend
        const errorData = await response.json();
        const errorMessage = errorData.detail || `Request failed with status ${response.status}`;
        throw new Error(errorMessage);
      }

      const data: { 
        score: number;
        matched_keywords: string[];
        missing_keywords: string[];
      } = await response.json();
      setSimilarityScore(data.score);
      setMatchedKeywords(data.matched_keywords || []);
      setMissingKeywords(data.missing_keywords || []);
    } catch (err) {
      console.error(err);
      // Display the actual error message from the backend
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to fetch similarity score from the server.');
      }
      setSimilarityScore(null);
      setMatchedKeywords([]);
      setMissingKeywords([]);
    } finally {
      setIsLoading(false);
    }
  };

  const isCheckDisabled = cvText.trim() === '' || jobDescText.trim() === '';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navbar />
      
      <main className="pt-20 pb-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* API Key Section */}
          <div className="mb-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-800">API Configuration</h2>
                <span className="text-xs text-gray-500">Optional</span>
              </div>
              <div className="space-y-2">
                <label htmlFor="api-key" className="block text-sm font-medium text-gray-700">
                  Gemini API Key
                </label>
                <input
                  id="api-key"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your API key (optional - uses .env if not provided)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                />
                <p className="text-xs text-gray-500">
                  If provided, this API key will be used instead of the one in the .env file. Leave empty to use the default.
                </p>
              </div>
            </div>
          </div>

          {/* Desktop and Mobile Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* CV Input */}
            <div className="lg:col-span-1">
              <InputBox
                title="CV Input"
                placeholder="Enter the CV information here..."
                value={cvText}
                onChange={setCvText}
                onClear={handleClearCV}
              />
            </div>

            {/* Job Description Input */}
            <div className="lg:col-span-1">
              <InputBox
                title="Job Description"
                placeholder="Enter the Job Description here...."
                value={jobDescText}
                onChange={setJobDescText}
                onClear={handleClearJobDesc}
              />
            </div>

            {/* Similarity Score */}
            <div className="lg:col-span-1">
              <SimilarityScore 
                score={similarityScore} 
                matchedKeywords={matchedKeywords}
                missingKeywords={missingKeywords}
              />
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
              {isCheckDisabled ? 'Enter Both Inputs' : isLoading ? 'Checking...' : 'Check Similarity'}
            </button>
          </div>

          {/* Error / Info Message */}
          <div className="mt-8 text-center">
            {error ? (
              <p className="text-sm text-red-500">{error}</p>
            ) : (
              <p className="text-sm text-gray-500">
                The similarity score is calculated using deterministic embedding-based analysis and keyword matching.
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
