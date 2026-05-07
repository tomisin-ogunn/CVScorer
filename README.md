# CVScorer Application

A modern, responsive single-page application for comparing CVs with Job Descriptions and displaying similarity scores.

## 📋 Overview

CVScorer now consists of a **frontend** (React/TypeScript) and a **backend** (FastAPI). The frontend provides an intuitive interface for HR professionals and recruiters to evaluate candidate CVs against job requirements, while the backend exposes an API that returns a (currently placeholder) similarity score.

**Note:** The similarity logic is still a placeholder. You can later replace the backend scoring implementation with real AI-powered analysis.

## 🧑‍💻 Roles:

- **Ahmed Bilal** [https://github.com/AhmedBilal449] – Developed backend functionality using FastAPI, implementing deterministic scoring with Gemini embeddings and cosine similarity for efficient data processing and retrieval.
- **Tomisin Ogunnusi** – Designed and developed an intuitive frontend interface using React.js, TypeScript, and Tailwind CSS improving usability and overall user experience.

## 🚀 Features

- **Dual Input System**: Separate text areas for CV and Job Description input
- **PDF Upload Support**: UI for PDF file selection (parsing to be implemented)
- **Similarity Scoring**: Visual display of match percentage with color-coded feedback
- **Responsive Design**: Optimized layouts for both desktop and mobile devices
- **Modern UI**: Clean, professional interface built with TailwindCSS
- **Type-Safe**: Written in TypeScript with strict type checking
- **Code Quality**: ESLint configuration for maintaining code standards

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS** - Utility-first CSS framework
- **Webpack 5** - Module bundler
- **ESLint** - Code linting and quality

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   ```

2. **Install frontend dependencies**
   ```bash
   cd CVScorer/frontend
   npm install
   ```

3. **(Optional) Set up backend environment**
   ```bash
   cd ../backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 🏃 Running the Application

### Frontend (Development Mode)
Start the frontend development server with hot reload:
```bash
cd CVScorer/frontend
npm start
```
The application will open automatically at `http://localhost:3000`.

### Backend (FastAPI)
In a separate terminal, from the backend folder:
```bash
cd CVScorer/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at `http://localhost:8000`.

### Frontend Production Build
Create an optimized production build:
```bash
npm run build
```
The build output will be in the `dist/` directory.

### Code Linting
Run ESLint to check code quality:
```bash
npm run lint
```

Fix linting issues automatically:
```bash
npm run lint:fix
```

## 📱 Usage

1. **Enter CV Data**: Type or paste CV content into the left text area
2. **Enter Job Description**: Type or paste job description into the middle text area
3. **Upload PDFs (Optional)**: Click "Upload PDF" buttons to select PDF files (displays filename only)
4. **Check Similarity**: Click the "Check Similarity" button to calculate the match score
5. **View Results**: The similarity score appears on the right with color-coded feedback:
   - 🟢 Green (80-100%): Excellent Match
   - 🟡 Yellow (60-79%): Good Match
   - 🟠 Orange (40-59%): Fair Match
   - 🔴 Red (0-39%): Poor Match

## 📐 Project Structure

Top-level (simplified):

```
cv-scorer-project/
└── CVScorer/
    ├── backend/                 # FastAPI backend
    └── frontend/                # React + TypeScript frontend
```

Frontend structure (this folder):

```
frontend/
├── public/
│   └── index.html                # HTML template
├── src/
│   ├── components/
│   │   ├── Navbar.tsx           # Top navigation bar
│   │   ├── InputBox.tsx         # Reusable input component
│   │   └── SimilarityScore.tsx  # Score display component
│   ├── App.tsx                  # Main application component
│   ├── index.tsx                # Application entry point
│   ├── index.css                # Global styles and Tailwind imports
│   └── global.d.ts              # Global type declarations
├── .eslintrc.js                 # ESLint configuration
├── tsconfig.json                # TypeScript configuration
├── tailwind.config.js           # TailwindCSS configuration
├── postcss.config.js            # PostCSS configuration
├── webpack.config.js            # Webpack configuration
├── package.json                 # Dependencies and scripts
└── README.md                    # This file
```

## 🎨 Design Features

- **Fixed Navigation**: Navbar stays at the top while scrolling
- **Gradient Backgrounds**: Modern gradient color schemes
- **Hover Effects**: Interactive button and card animations
- **Focus States**: Accessibility-friendly focus indicators
- **Responsive Grid**: 3-column desktop layout that stacks on mobile
- **Shadow Effects**: Depth and hierarchy through subtle shadows

## 🔧 Configuration

### TypeScript
The project uses strict TypeScript settings with:
- Strict mode enabled
- No unused locals/parameters warnings
- Path aliases configured (`@/` → `src/`)

### Linting
ESLint is configured with:
- React and React Hooks rules
- TypeScript-specific rules
- Automatic React version detection

### TailwindCSS
Custom theme extends include:
- Primary color palette (blue shades)
- Inter font family

## 🧪 Testing Requirements (To Be Implemented)

Future testing should verify:
- ✅ All UI elements render correctly on desktop and mobile
- ✅ Clear buttons empty their respective text areas
- ✅ Upload PDF buttons open file selector and display filename
- ✅ Check button is disabled when inputs are empty
- ✅ Similarity score updates when Check button is clicked
- ✅ Text areas are scrollable with overflow content

## 👨‍💻 Development

### Prerequisites
- Node.js 16+ and npm
- Modern web browser with ES2020 support

### Code Style
- Use functional components with hooks
- Follow TypeScript strict mode
- Use TailwindCSS utility classes
- Keep components small and focused
- Write descriptive prop types

## 👤 Author

**Ahmed Bilal, Tomisin Ogunnusi**  
Date: May 07, 2026



---
