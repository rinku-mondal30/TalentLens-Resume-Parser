# TalentLens AI — Resume Parser

## Requirements
- Python 3.10–3.12 recommended
- Internet connection for installing packages and downloading the spaCy model
- Tesseract OCR is needed for JPG/JPEG image resumes. PDF text extraction works without it.

## Setup (Windows)
1. Extract the ZIP folder.
2. Open Command Prompt or VS Code terminal inside `resume_parser_project`.
3. Create a virtual environment:
   `py -m venv .venv`
4. Activate it:
   `.venv\Scripts\activate`
5. Install packages:
   `python -m pip install --upgrade pip`
   `pip install -r requirements.txt`
6. Download the English spaCy model:
   `python -m spacy download en_core_web_sm`
7. Start the app:
   `python app.py`
8. Open `http://127.0.0.1:5000` in your browser.
9. Click Get started, create an account with your name, email, and password (8+ characters), then log in.

## JPG/JPEG OCR setup (Windows)
1. Install Tesseract OCR for Windows from its official UB Mannheim installer page: https://github.com/UB-Mannheim/tesseract/wiki
2. If Python cannot find it, add the Tesseract install folder to PATH or add this line near the imports in `app.py` (change the path if needed):
   `pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`
3. Restart the terminal and app.

## Project structure
- `app.py` — Flask routes, login/register/logout, text extraction and NLP parsing
- `templates/` — HTML pages
- `static/style.css` — responsive professional design
- `uploads/` — uploaded resumes
- `users.db` — created automatically for account storage

## Notes
- Passwords are stored as hashes, not plain text.
- This is a local student project, not a production HR system. Add CSRF protection, stronger session configuration, file scanning, access controls, and retention rules before public deployment.
- Name detection and skills matching are basic demonstrations; verify extracted information manually.
- Only upload resumes you have permission to process.
- Stop the local server with `Ctrl+C` in the terminal.


### Download parsed results as PDF
After uploading a resume and viewing the parsed result on the dashboard, click **Download result as PDF**. The report includes candidate details, detected contact information, skills, education keywords, qualification, experience, and the uploaded filename. CSV download remains available too.
