# QUBIX – Smart Document Verification System

QUBIX is an intelligent, multi-tier document verification system designed to determine whether applicants have uploaded all required, valid, consistent, and unaltered documents for any jurisdictional service or certificate.

---

## 🌟 Key Features

1. **User Authentication & RBAC**: Secure JWT authentication with role-based access for applicants and administrators.
2. **Encrypted Document Ingestion**: Supports PDF, JPG, JPEG, and PNG files with magic byte validation, size enforcement, and AES-256 encryption at rest.
3. **AI-Powered OCR & Field Extraction**: High-fidelity text extraction via PyMuPDF vector processing and pluggable OCR, extracting names, birth dates, document numbers, issue/expiry dates, and addresses.
4. **Configurable Requirement Matrix**: Dynamic checklists for multiple jurisdictions (Passport Application, Driver's License Renewal, Employment Onboarding) that automatically identify satisfied vs. missing documents and generate next actions.
5. **Deterministic Expiry Detection**: Rigorous temporal evaluation against reference dates (`VALID`, `EXPIRING_SOON`, `EXPIRED`, `EXPIRY_DATE_NOT_FOUND`) with zero date hallucination.
6. **Cross-Document Mismatch Detection**: Fuzzy string matching, token permutation analysis, and date conflict detection across all uploaded files in a bundle.
7. **Forensic Image Tampering Screening**: Error Level Analysis (ELA) and metadata inspection for photo-editing tools (Photoshop, Canva, GIMP) with explainable flags for human review.
8. **Automated PDF Verification Reports**: Generates formal audit reports with compliance statuses (`COMPLETE`, `INCOMPLETE`, `REVIEW_REQUIRED`), checklist breakdowns, and auditor sign-off sections.
9. **Modern React & Tailwind Dashboard**: Responsive user interface with real-time feedback, human-in-the-loop OCR correction modal, and admin adjudication portal.

---

## 📁 Repository Structure

```
docverify-ai/
├── start_app.bat                  # One-click Windows starter script
├── pytest.ini                     # Pytest configuration
├── backend/
│   ├── app/
│   │   ├── config.py              # Configuration & Pydantic settings
│   │   ├── database.py            # Database engine & session
│   │   ├── main.py                # FastAPI app initialization
│   │   ├── models/                # SQLAlchemy ORM models
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── routers/               # API endpoints (auth, apps, docs, verify, admin)
│   │   ├── services/              # Business logic (OCR, expiry, mismatch, tamper, PDF)
│   │   └── utils/                 # Security, encryption, and date parsing
│   ├── tests/                     # Unit and integration test suite
│   ├── test_api_endpoints.py      # End-to-end API test suite
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment variables template
│   └── Dockerfile                 # Production backend container definition
├── frontend/
│   ├── src/
│   │   ├── components/            # UI components (Checklist, Badges, Uploader, Alerts)
│   │   ├── pages/                 # React views (Login, Register, Dashboard, Cockpit, Admin)
│   │   ├── context/               # AuthContext state management
│   │   └── services/              # Axios API client
│   ├── package.json               # Node.js dependencies
│   ├── vite.config.js             # Vite configuration
│   └── dist/                      # Pre-built production assets
├── storage/                       # Encrypted document and report storage
├── docs/
│   ├── ARCHITECTURE.md            # Detailed system architecture
│   ├── DATABASE_SCHEMA.md         # Database schema & ER diagram
│   ├── API_SPEC.md                # REST API documentation
│   └── SETUP_GUIDE.md             # Installation & deployment instructions
└── docker-compose.yml             # Multi-container orchestration
```

---

## ⚡ One-Click Startup (Windows)

Simply double-click:
```
start_app.bat
```
This batch script automatically:
1. Detects Python 3.11+ and Node.js LTS in system paths.
2. Creates the Python virtual environment (`backend\venv`) and `.env` configuration.
3. Installs backend dependencies from `backend\requirements.txt`.
4. Installs frontend dependencies via `npm install`.
5. Launches the **FastAPI Backend** on `http://127.0.0.1:8000`.
6. Launches the **React Vite Frontend** on `http://localhost:5173`.
7. Automatically opens `http://localhost:5173` in your default browser.

---

## 💻 Manual Setup Instructions (Windows PowerShell)

### Step 1: Run Backend
Open a PowerShell window:
```powershell
cd backend

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Step 2: Run Frontend
Open a second PowerShell window:
```powershell
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Testing & Verification

### Run Automated Backend Unit Tests
```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests -v
```
*All 12 unit tests pass covering Authentication, Expiry, Mismatches, Tampering, and Checklist requirements.*

### Run End-to-End API Pipeline Test
```powershell
cd backend
.\venv\Scripts\python.exe test_api_endpoints.py
```
*Verifies registration, login, application creation, PDF document upload, OCR extraction, requirement matrix checking, and downloadable PDF report generation.*

### Run Frontend Production Build Check
```powershell
cd frontend
npm run build
```
