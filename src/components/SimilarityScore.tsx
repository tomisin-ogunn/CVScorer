import React from 'react';

interface SimilarityScoreProps {
  score: number | null;
}

const SimilarityScore: React.FC<SimilarityScoreProps> = ({ score }) => {
  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    if (score >= 40) return 'bg-orange-50 border-orange-200';
    return 'bg-red-50 border-red-200';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Poor Match';
  };

  return (
    <div className="bg-white rounded-lg shadow-md flex flex-col h-full">
      <div className="px-4 py-3 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 rounded-t-lg">
        <h2 className="text-lg font-semibold text-gray-800">Similarity Score</h2>
      </div>
      
      <div className="flex-1 flex items-center justify-center p-6">
        {score !== null ? (
          <div className={`w-full p-6 rounded-lg border-2 ${getScoreBgColor(score)} transition-all duration-300`}>
            <div className="text-center">
              <div className={`text-6xl font-bold ${getScoreColor(score)} mb-2`}>
                {score}%
              </div>
              <div className={`text-lg font-medium ${getScoreColor(score)}`}>
                {getScoreLabel(score)}
              </div>
              <div className="mt-4 text-sm text-gray-600">
                Match Confidence
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-400">
            <svg
              className="mx-auto h-16 w-16 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <p className="text-lg font-medium">No Score Yet</p>
            <p className="text-sm mt-2">Click "Check" to calculate similarity</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SimilarityScore;
