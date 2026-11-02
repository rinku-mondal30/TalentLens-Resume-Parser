import os, re, sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import spacy
import fitz
from PIL import Image
import pytesseract
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-for-local-development")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg"}
DB_PATH = os.path.join(BASE_DIR, "users.db")

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )""")

init_db()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(path):
    ext = path.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    # OCR for JPG/JPEG requires the Tesseract program to be installed separately.
    return pytesseract.image_to_string(Image.open(path))

def parse_resume(text):
    emails = re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text)
    phones = re.findall(r'(?<!\d)(?:\+?\d[\d\s()\-]{8,}\d)(?!\d)', text)
    names = []
    if nlp:
        doc = nlp(text[:100000])
        names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    skill_bank = [
        "Python", "Java", "C", "C++", "SQL", "Machine Learning",
        "Deep Learning", "NLP", "HTML", "CSS", "JavaScript", "Pandas",
        "NumPy", "Flask", "Django", "TensorFlow", "PyTorch", "Excel",
        "Data Analysis", "Communication", "Project Management"
    ]
    skills = [s for s in skill_bank if re.search(r"\b" + re.escape(s) + r"\b", text, re.I)]
    education_bank = ["B.Tech", "B.E.", "B.Sc", "M.Tech", "M.Sc", "MBA", "BCA", "MCA", "Ph.D", "Bachelor", "Master", "Diploma", "Higher Secondary"]
    education = [e for e in education_bank if re.search(re.escape(e), text, re.I)]
    return {
        "Detected name": names[0] if names else "Not confidently detected",
        "Email": emails[0] if emails else "Not found",
        "Phone": phones[0] if phones else "Not found",
        "Skills": ", ".join(skills) if skills else "No listed skills detected",
        "Education keywords": ", ".join(education) if education else "No listed qualification detected",
        "Extracted text": text[:12000] if text.strip() else "No text detected. For a scanned PDF, OCR may be needed."
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name and email. Password must be at least 8 characters.", "danger")
            return render_template("register.html")
        try:
            with db() as con:
                cur = con.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                                  (name, email, generate_password_hash(password)))
                user_id = cur.lastrowid
            session["user_id"] = user_id
            session["name"] = name
            session["email"] = email
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("That email is already registered. Please log in.", "warning")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    result = None
    candidate = {}
    if request.method == "POST":
        candidate = {
            "candidate_name": request.form.get("candidate_name", "").strip(),
            "candidate_email": request.form.get("candidate_email", "").strip(),
            "qualification": request.form.get("qualification", "").strip(),
            "status": request.form.get("status", "").strip(),
            "experience": request.form.get("experience", "").strip()
        }
        uploaded = request.files.get("resume")
        if not candidate["candidate_name"] or not candidate["qualification"] or not candidate["status"]:
            flash("Please complete the required candidate fields.", "danger")
        elif not uploaded or uploaded.filename == "":
            flash("Please select a PDF, JPG, or JPEG resume.", "danger")
        elif not allowed_file(uploaded.filename):
            flash("Unsupported file type. Upload PDF, JPG, or JPEG only.", "danger")
        else:
            safe_name = secure_filename(uploaded.filename)
            saved_name = f'{session["user_id"]}_{safe_name}'
            path = os.path.join(app.config["UPLOAD_FOLDER"], saved_name)
            uploaded.save(path)
            try:
                text = extract_text(path)
                result = parse_resume(text)
                result["Uploaded file"] = safe_name
                result["Candidate name (form)"] = candidate["candidate_name"]
                result["Candidate email (form)"] = candidate["candidate_email"] or "Not provided"
                result["Current qualification (form)"] = candidate["qualification"]
                result["Candidate type"] = candidate["status"].title()
                result["Experience (form)"] = candidate["experience"] or ("Not applicable" if candidate["status"] == "fresher" else "Not provided")
                # Keep the compact fields in the session; extracted text can exceed cookie limits.
                session["last_result"] = {k: v for k, v in result.items() if k != "Extracted text"}
                session["last_candidate"] = candidate
            except Exception as exc:
                flash("Could not read this file. For JPG/JPEG, install Tesseract OCR and restart the app. Details: " + str(exc)[:180], "danger")
    return render_template("dashboard.html", result=result, candidate=candidate)

@app.route("/download-pdf")
@login_required
def download_pdf():
    result = session.get("last_result")
    if not result:
        flash("Please parse a resume first, then download its PDF report.", "warning")
        return redirect(url_for("dashboard"))

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm, title="TalentLens Resume Parsing Report"
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=21, leading=26, textColor=colors.HexColor("#183b56"),
        alignment=TA_CENTER, spaceAfter=5*mm
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle", parent=styles["Normal"], alignment=TA_CENTER,
        textColor=colors.HexColor("#527080"), fontSize=9, spaceAfter=8*mm
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", parent=styles["Heading2"], fontSize=12,
        textColor=colors.HexColor("#146c94"), spaceBefore=4*mm, spaceAfter=2*mm
    ))
    story = [
        Paragraph("TalentLens AI", styles["ReportTitle"]),
        Paragraph("Resume Parsing Report · Generated by spaCy NLP", styles["ReportSubtitle"]),
        Paragraph("Candidate summary", styles["SectionHeading"]),
    ]

    def safe(value):
        from xml.sax.saxutils import escape
        return escape(str(value if value not in (None, "") else "Not provided")).replace("\n", "<br/>")

    preferred = [
        "Candidate name (form)", "Candidate email (form)", "Detected name", "Email", "Phone",
        "Candidate type", "Current qualification (form)", "Experience (form)", "Skills",
        "Education keywords", "Uploaded file"
    ]
    rows = [[Paragraph("<b>Field</b>", styles["BodyText"]), Paragraph("<b>Extracted result</b>", styles["BodyText"])]]
    for key in preferred:
        if key in result:
            rows.append([Paragraph(safe(key), styles["BodyText"]), Paragraph(safe(result[key]), styles["BodyText"])])
    table = Table(rows, colWidths=[52*mm, 108*mm], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f2f7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#183b56")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d5e1e8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.extend([Spacer(1, 7*mm), Paragraph("Important note", styles["SectionHeading"]),
        Paragraph("This report contains automatically extracted information. Please verify names, contact details, skills and qualifications against the original resume. Results may be incomplete, especially for scanned or unusually formatted documents.", styles["BodyText"])])
    doc.build(story)
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = 'attachment; filename="resume_parsing_report.pdf"'
    return response

@app.errorhandler(413)
def too_large(_error):
    flash("File is too large. Maximum upload size is 8 MB.", "danger")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
