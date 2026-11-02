# TalentLens AI – Resume Parser

An AI-powered Resume Parser built using **Python, Flask, spaCy NLP, and Machine Learning concepts**. The application extracts important information from resumes and generates a structured PDF report.

## Features

- User registration and login system
- Separate dashboard for resume processing
- Resume upload and text extraction
- NLP-based information extraction using spaCy
- Candidate name and contact information detection
- Skills and education keyword extraction
- Fresher and experienced candidate selection
- Download parsed resume results as PDF
- Responsive and user-friendly interface

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| spaCy | Natural Language Processing |
| PyMuPDF | PDF text extraction |
| Pytesseract | OCR for image resumes |
| HTML | Web page structure |
| CSS | Website styling |
| SQLite | User data storage |

## Project Structure

```text
TalentLens_Resume_Parser_PDF_Only/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   └── style.css
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
├── uploads/       # Uploaded resumes (created when needed)
└── users.db       # Database (created when needed)
```

## Requirements

- Python 3.10–3.12 recommended
- Git
- VS Code (recommended)
- Internet connection for installing packages and downloading the spaCy model
- Tesseract OCR for JPG/JPEG image resume processing

## Installation and Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/rinku-mondal30/TalentLens-Resume-Parser.git
```

### Step 2: Open the project folder

```bash
cd TalentLens-Resume-Parser
```

### Step 3: Create a virtual environment

```bash
python -m venv .venv
```

### Step 4: Activate the virtual environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Download the spaCy English model

```bash
python -m spacy download en_core_web_sm
```

### Step 7: Run the application

```bash
python app.py
```

### Step 8: Open the application

Open your browser and visit:

http://127.0.0.1:5000

Register an account, log in, select your qualification status, and upload git add README.mda resume.

## Tesseract OCR Setup

Tesseract OCR is required for extracting text from JPG/JPEG image resumes.

1. Download the Windows installer from the [Tesseract OCR repository](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install Tesseract OCR.
3. If Python cannot locate it, configure the executable path in your application:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

4. Restart your terminal and Flask application.

PDF text extraction does not require Tesseract when the PDF contains extractable text.

## Download Parsed Results

After uploading a resume:

1. Open the dashboard.
2. View the extracted candidate information.
3. Review the detected skills, education, and experience details.
4. Click **Download Result as PDF** to download the parsed report.

## Future Improvements

- Advanced Named Entity Recognition (NER)
- Improved skills classification
- Resume ranking and job matching
- Support for additional resume formats
- Cloud deployment
- Admin dashboard and analytics

## Important Notes

- Do not upload passwords, secret keys, database files, or private resumes to a public GitHub repository.
- Passwords should be stored securely as hashes.
- This project is an academic demonstration, not a production-ready HR system.
- Extracted information should be manually verified.
- Only upload resumes you have permission to process.

## Author

**Rinku Mondal**

GitHub: [rinku-mondal30](https://github.com/rinku-mondal30)

## License

This project is intended for educational and learning purposes.

