# DocVerify AI – Setup, Installation & Deployment Guide

## 1. Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12
- **Node.js**: Version 18.x or 20.x
- **Package Managers**: `pip` and `npm`
- **Optional System Binaries**: Tesseract OCR (if using local optical character recognition for scanned raster images)

---

## 2. Backend Setup

### 2.1 Virtual Environment
```bash
cd backend
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Linux / macOS:
source venv/bin/activate
```

### 2.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.3 Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default parameters in `.env`:
- `DATABASE_URL`: `sqlite:///./docverify.db` (Default zero-config SQLite)
- `SECRET_KEY`: Set to a cryptographically secure 32+ character random string in production.
- `ENCRYPTION_KEY`: Set to a 32-byte base64 string for AES-256 storage encryption.
- `STORAGE_ROOT`: `../storage`

### 2.4 Initialize Database & Seed Profiles
Tables and default requirement profiles (Passport, Driver License, Employment Onboarding) are automatically seeded on application startup.

To start the FastAPI development server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive API documentation will be available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 3. Frontend Setup

### 3.1 Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

### 3.2 Run the Development Server
```bash
npm run dev
```
The React application dashboard will be accessible at:
`http://localhost:5173`

---

## 4. Generating Synthetic Test Documents
To generate synthetic test documents (valid passport, expired passport, utility bill proof of address, conflicting ID card, and Photoshop-tagged tampered image):
```bash
cd backend
python -m tests.create_sample_docs
```
Output files will be saved in `backend/tests/sample_docs/`:
- `passport_valid.pdf` (Valid until 2030)
- `passport_expired.pdf` (Expired in 2021)
- `utility_bill.pdf` (Proof of Address)
- `id_card_mismatch.png` (Conflicting birth date)
- `id_card_tampered.png` (Photoshop metadata flag)

---

## 5. Running Automated Tests
Run pytest across all modules:
```bash
cd backend
pytest tests -v
```

Tests cover:
- Authentication, JWT, and AES encryption (`test_auth.py`)
- OCR rule classification and zero date hallucination (`test_ocr.py`)
- Configurable checklist fulfillment and missing doc detection (`test_requirements.py`)
- Expiry calculation and non-expiring doc categories (`test_expiry.py`)
- Cross-document name and DOB mismatch engine (`test_mismatch.py`)
- Metadata and Error Level Analysis (ELA) tampering screening (`test_tampering.py`)

---

## 6. Docker Deployment (Production)

To launch the full production stack (FastAPI Backend + PostgreSQL + React Frontend + OCR Libraries):
```bash
docker-compose up --build -d
```
Services started:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`
