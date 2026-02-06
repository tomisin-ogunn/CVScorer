import React, { useRef, ChangeEvent } from 'react';

interface InputBoxProps {
  title: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
}

const InputBox: React.FC<InputBoxProps> = ({
  title,
  placeholder,
  value,
  onChange,
  onClear,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTextChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onChange(`[File Selected: ${file.name}]\n\n(PDF parsing not yet implemented)`);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="bg-white rounded-lg shadow-md flex flex-col h-full">
        <div className="px-4 py-3 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 rounded-t-lg">
          <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
        </div>
        
        <div className="flex-1 p-4">
          <textarea
            value={value}
            onChange={handleTextChange}
            placeholder={placeholder}
            className="w-full h-full min-h-[300px] p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-all duration-200 text-gray-700 placeholder-gray-400"
            aria-label={title}
          />
        </div>

        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 rounded-b-lg flex flex-wrap gap-3">
          <button
            onClick={onClear}
            className="px-5 py-2.5 bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            aria-label={`Clear ${title}`}
          >
            Clear
          </button>
          
          <button
            onClick={handleFileClick}
            className="px-5 py-2.5 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            aria-label={`Upload PDF for ${title}`}
          >
            Upload PDF
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
            aria-hidden="true"
          />
        </div>
      </div>
    </div>
  );
};

export default InputBox;
