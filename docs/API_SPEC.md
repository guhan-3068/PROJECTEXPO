# DocVerify AI – REST API Specification

Base URL: `/api/v1`

---

## 1. Authentication Endpoints (`/auth`)

### 1.1 User Registration
- **Method & Path**: `POST /api/v1/auth/register`
- **Request Body**:
  ```json
  {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "password": "StrongPassword123!",
    "role": "USER"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "c1f7b8a2-...",
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "role": "USER",
    "is_active": true,
    "created_at": "2026-10-25T09:00:00Z"
  }
  ```

### 1.2 User Login
- **Method & Path**: `POST /api/v1/auth/login`
- **Request Body**:
  ```json
  {
    "email": "jane@example.com",
    "password": "StrongPassword123!"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { ... }
  }
  ```

### 1.3 Current User Info
- **Method & Path**: `GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`

---

## 2. Applications & Checklists (`/applications`)

### 2.1 List Configured Application Profiles
- **Method & Path**: `GET /api/v1/applications/profiles`
- **Description**: Returns all configurable checklist matrices (e.g. Passport, Driver License, Employment Screening) along with mandatory and optional items.

### 2.2 Start an Application
- **Method & Path**: `POST /api/v1/applications/start`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "application_profile_id": "profile-uuid",
    "consent_given": true
  }
  ```
- **Response**: `201 Created` with unique reference number `APP-202610-A9B2C1`.

### 2.3 Get User's Applications
- **Method & Path**: `GET /api/v1/applications/my`
- **Headers**: `Authorization: Bearer <token>`

---

## 3. Document Management & OCR (`/documents`)

### 3.1 Upload Documents
- **Method & Path**: `POST /api/v1/documents/upload/{application_id}`
- **Headers**: `Authorization: Bearer <token>`, `Content-Type: multipart/form-data`
- **Form Data**:
  - `files`: File[] (PDF, JPG, JPEG, PNG)
  - `claimed_category`: string (optional)
- **Processing**:
  - Validates magic signatures & size
  - Encrypts via AES-256 at rest
  - Runs OCR
  - Performs rule-based entity extraction
  - Performs forensic ELA & metadata check
- **Response**: `200 OK` (Array of document records with extracted fields and confidence).

### 3.2 Human-in-the-Loop OCR Field Correction
- **Method & Path**: `PUT /api/v1/documents/{document_id}/fields`
- **Request Body**:
  ```json
  {
    "field_key": "full_name",
    "corrected_value": "Jane Marie Doe",
    "notes": "Fixed OCR abbreviation"
  }
  ```

### 3.3 Decrypt & Stream Document
- **Method & Path**: `GET /api/v1/documents/{document_id}/download`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` (Streamed decrypted file).

---

## 4. Verification Engine (`/verify`)

### 4.1 Execute Verification Pipeline
- **Method & Path**: `POST /api/v1/verify/run/{application_id}`
- **Description**: Orchestrates the requirement checker, temporal expiry evaluator, cross-document entity mismatch engine, and tampering screening. Generates the downloadable PDF audit report.
- **Response**:
  ```json
  {
    "id": "result-uuid",
    "overall_status": "COMPLETE | INCOMPLETE | REVIEW_REQUIRED",
    "satisfied_requirements": [ ... ],
    "missing_requirements": [ ... ],
    "expired_documents": [ ... ],
    "expiring_soon_documents": [ ... ],
    "detected_mismatches": [ ... ],
    "tampering_flags": [ ... ],
    "recommended_actions": [ ... ],
    "report_pdf_url": "/api/v1/reports/{application_id}/download",
    "evaluated_at": "2026-10-25T09:30:00Z"
  }
  ```

---

## 5. Official Reports (`/reports`)

### 5.1 Download PDF Verification Report
- **Method & Path**: `GET /api/v1/reports/{application_id}/download`
- **Response**: Binary `application/pdf` with Content-Disposition attachment.

---

## 6. Administrator Review (`/admin`)

### 6.1 Review Queue
- **Method & Path**: `GET /api/v1/admin/applications?status_filter=REVIEW_REQUIRED`
- **Requires**: `ADMIN` role.

### 6.2 Submit Adjudication Determination
- **Method & Path**: `POST /api/v1/admin/review/{application_id}`
- **Request Body**:
  ```json
  {
    "new_status": "APPROVED",
    "review_notes": "Physical original verified in person; name variation explained by marriage certificate."
  }
  ```
