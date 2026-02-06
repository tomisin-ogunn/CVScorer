# CV Matcher

A React-based front-end application for checking similarity between CVs and Job Descriptions.

## Features

- **Dual Input Interface**: Side-by-side text areas for CV and Job Description input
- **PDF Upload Support**: Upload PDF files for both CV and Job Description (displays file name)
- **Clear Functionality**: Reset individual text areas with dedicated clear buttons
- **Similarity Score Display**: View matching score in a dedicated panel
- **Responsive Design**: Built with TailwindCSS for a modern, responsive layout
- **Clean UI**: Fixed navbar, well-organized layout with proper spacing

## Tech Stack

- **React.js** (v18.2.0)
- **TailwindCSS** (v3.4.0)
- **React Scripts** (v5.0.1)

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CVScorer
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open your browser and navigate to:
```
http://localhost:3000
```

## Project Structure

```
CVScorer/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── CVMatcher.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

## Available Scripts

### `npm start`
Runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

### `npm run build`
Builds the app for production to the `build` folder.

### `npm test`
Launches the test runner in interactive watch mode.

## Usage

1. **Input CV Data**: Type or paste CV content in the left text area, or upload a PDF file
2. **Input Job Description**: Type or paste job description in the right text area, or upload a PDF file
3. **Click Check**: Press the "Check Similarity" button at the bottom
4. **View Results**: The similarity score will appear in the right panel (currently shows a placeholder 85%)

## Current Implementation

This is a **front-end only** implementation with the following placeholder functionality:

- PDF upload displays the file name but doesn't parse content
- Check button returns a static similarity score (85%)
- No backend integration or AI processing

## Future Enhancements

- Backend integration for actual similarity calculation
- PDF parsing and text extraction
- AI-powered matching algorithm
- Detailed match breakdown
- Export results functionality

## Author

Ahmed Bilal

## Date

6 Feb 2026
