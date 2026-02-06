Product Requirement Document (PRD)

Project: CV & Job Description Similarity Checker
Prepared For: Claude AI / Development Team
Prepared By: Ahmed Bilal
Date: 6 Feb 2026

1. Objective

Create a single-page web application that allows users to input a CV and a Job Description, either by typing or uploading PDFs, and calculate a similarity score between them. The UI should be clean, simple, and intuitive, using React.js and TailwindCSS.

2. Target Users

Job seekers who want to tailor their CVs to specific job descriptions.

Recruiters who want a quick comparison of CVs against job descriptions.

3. Functional Requirements
3.1 Layout & UI

Navbar at the top with project title (e.g., "CV Matcher").

Main Page: Split into two primary columns:

Left Column:

CV Input Box (large, multiline text area)

Placeholder text: Input CV Data

Clear Button to empty the text box.

Upload PDF Button to populate the box with PDF content.

Middle Column:

Job Description Input Box (large, multiline text area)

Placeholder text: Input Job Description

Clear Button to empty the text box.

Upload PDF Button to populate the box with PDF content.

Right Column:

Similarity Score Box (read-only) to display the calculated similarity.

Bottom Section:

Check Button: When clicked, computes similarity between the CV and job description.

3.2 Functionality

Clear Button: Resets the corresponding input box.

Upload PDF:

Allows user to upload a PDF file.

Extracts text and populates the corresponding input box.

Acceptable file format: .pdf.

Check Button:

Sends the CV and Job Description text to backend (or local function for MVP).

Returns a similarity score (e.g., 0–100%).

Displays score in the Similarity Score Box.

4. Non-Functional Requirements

Frameworks & Tools:

React.js for front-end.

TailwindCSS for styling.

Responsiveness: Layout should adapt to different screen sizes.

Accessibility: Buttons and inputs should be keyboard-accessible.

Performance: Page should load quickly and handle moderately large text inputs.

5. Phase 1 – MVP Scope

Single-page layout with side-by-side input boxes.

Clear buttons for each input box.

Upload PDF functionality (text extraction only).

Similarity Score box (placeholder for backend integration).

Check button triggers placeholder function that can later be connected to AI similarity engine.

6. Phase 2 – Enhancements

Real-time similarity calculation as user types.

Highlighting matched keywords between CV and job description.

Historical comparisons and score tracking.

User authentication and account management.

Downloadable similarity report as PDF.

7. UI Mockup (Textual)
---------------------------------------------
| Navbar: CV Matcher                        |
---------------------------------------------
| CV Input Box           | Job Description Box  | Similarity Score |
| [Text Area]            | [Text Area]         | [Score: 85%]    |
| [Clear] [Upload PDF]   | [Clear] [Upload PDF]|                 |
---------------------------------------------
|                             [Check] Button |
---------------------------------------------

8. Deliverables

React.js frontend code for single-page application.

TailwindCSS styling matching layout and design requirements.

Functional buttons (Clear, Upload PDF, Check).

Placeholder Similarity Score logic.