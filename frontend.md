Product Requirements Document (PRD)

Project: CV Matcher Front-End
Prepared By: Ahmed Bilal, Tomisin Ogunnusi
Date: 6 Feb 2026

1. Objective

Create a single-page front-end application that allows users to input CVs and Job Descriptions, compare them, and display a similarity score. This stage focuses on layout, styling, and user interactions only. No backend or AI logic is required.

2. Target Users

HR professionals evaluating candidates.

Recruiters comparing CVs to job descriptions.

Developers and testers for the initial front-end prototype.

3. Scope

Implemented in React.js with TypeScript.

Styling with TailwindCSS.

Front-end only; placeholder interactions.

Includes linting configuration for code quality.

Excluded:

Actual AI or backend similarity computation.

PDF parsing beyond displaying file names.

4. Functional Requirements
4.1 Navbar

Fixed at the top of the page.

Displays project title: “CV Matcher”.

4.2 Main Section
4.2.1 CV Input Box (Left)

Large multiline text area.

Placeholder: "Input CV Data".

Scrollable if content overflows.

Buttons below:

Clear → resets text area to empty.

Upload PDF → opens file selection; displays selected file name in the text area.

4.2.2 Job Description Input Box (Right)

Large multiline text area.

Placeholder: "Input Job Description".

Scrollable if content overflows.

Buttons below:

Clear → resets text area to empty.

Upload PDF → opens file selection; displays selected file name in the text area.

4.2.3 Similarity Score Box

Positioned on the right side of the page (desktop view).

Read-only display.

Initially empty.

Populated with a static placeholder number (e.g., 85%) when Check button is clicked.

4.3 Bottom Section

Check Button centered below input boxes.

Triggers a placeholder function: updates similarity score box with static value.

5. Non-Functional Requirements

Responsive design using TailwindCSS.

Consistent and visually distinct buttons (Clear, Upload PDF, Check).

Large input boxes visually suggest capacity for long text.

Smooth user experience with no page reloads.

Linted TypeScript codebase following best practices.

6. Layout and UX Requirements

Desktop Layout:

------------------------------------------------------
| Navbar: CV Matcher                               |
------------------------------------------------------
| CV Input          | Job Description Input        | Similarity Score
| [Text Area]       | [Text Area]                  | [Read-only Box]
| [Clear][Upload]   | [Clear][Upload]             |
------------------------------------------------------
|                  [Check Button Centered]        |
------------------------------------------------------


Mobile Layout:

Stack CV input, Job Description input, and Similarity Score vertically.

Buttons remain directly below their corresponding inputs.

7. Interactions

Clear Buttons: empties the respective text area.

Upload PDF Buttons: opens file selector; displays file name in the respective input area (no parsing yet).

Check Button: triggers placeholder function; updates similarity score box with a static value.

8. Acceptance Criteria

All UI elements render correctly on desktop and mobile.

Buttons respond as expected (Clear, Upload PDF, Check).

Text areas are scrollable when content overflows.

Similarity score box updates on Check button click with placeholder value.

Code follows TypeScript with linting enabled.

9. Future Considerations (Out of Scope)

Integrating AI/ML-based similarity analysis.

Parsing PDF content into text areas.

Saving or exporting results.