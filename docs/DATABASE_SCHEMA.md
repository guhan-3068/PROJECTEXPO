# DocVerify AI – Database Schema Design

## 1. Entity-Relationship Overview

```mermaid
erDiagram
    USERS ||--o{ USER_APPLICATIONS : "submits"
    USERS ||--o{ AUDIT_LOGS : "triggers"
    USERS ||--o{ ADMIN_REVIEWS : "performs"
    
    APPLICATION_PROFILES ||--o{ CHECKLIST_REQUIREMENTS : "defines"
    APPLICATION_PROFILES ||--o{ USER_APPLICATIONS : "governs"
    
    USER_APPLICATIONS ||--o{ UPLOADED_DOCUMENTS : "contains"
    USER_APPLICATIONS ||--o| VERIFICATION_RESULTS : "produces"
    USER_APPLICATIONS ||--o{ ADMIN_REVIEWS : "receives"
    
    UPLOADED_DOCUMENTS ||--o{ EXTRACTED_FIELDS : "yields"
    UPLOADED_DOCUMENTS ||--o| TAMPERING_ANALYSES : "evaluated_by"
    
    USERS {
        uuid id PK
        varchar email UK
        varchar hashed_password
        varchar full_name
        varchar role "USER | ADMIN | AUDITOR"
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    APPLICATION_PROFILES {
        uuid id PK
        varchar code UK "e.g. US_PASSPORT"
        varchar name
        varchar jurisdiction "e.g. US, UK, IN, GLOBAL"
        varchar category
        text description
        boolean is_active
        timestamp created_at
    }

    CHECKLIST_REQUIREMENTS {
        uuid id PK
        uuid application_profile_id FK
        varchar requirement_code "e.g. PROOF_OF_ID"
        varchar display_name
        text description
        boolean is_mandatory
        json accepted_categories "['PASSPORT', 'NATIONAL_ID']"
        integer min_validity_days "Default: 0"
        boolean allow_manual_override
        integer sort_order
    }

    USER_APPLICATIONS {
        uuid id PK
        uuid user_id FK
        uuid application_profile_id FK
        varchar reference_number UK
        varchar status "DRAFT | SUBMITTED | INCOMPLETE | REVIEW_REQUIRED | APPROVED | REJECTED"
        boolean consent_given
        timestamp consent_timestamp
        timestamp created_at
        timestamp updated_at
    }

    UPLOADED_DOCUMENTS {
        uuid id PK
        uuid user_application_id FK
        uuid user_id FK
        varchar original_filename
        varchar stored_filename
        varchar file_path
        integer file_size_bytes
        varchar mime_type
        varchar file_hash_sha256
        boolean is_encrypted
        varchar doc_category "PASSPORT | NATIONAL_ID | UTILITY_BILL | etc."
        varchar ocr_status "PENDING | SUCCESS | FAILED"
        float ocr_overall_confidence
        text raw_text
        timestamp created_at
    }

    EXTRACTED_FIELDS {
        uuid id PK
        uuid document_id FK
        varchar field_key "full_name | dob | doc_number | expiry_date | issue_date"
        varchar raw_value
        varchar normalized_value
        float confidence
        boolean is_user_corrected
        varchar corrected_value
        varchar notes
        timestamp created_at
        timestamp updated_at
    }

    TAMPERING_ANALYSES {
        uuid id PK
        uuid document_id FK UK
        boolean is_flagged
        varchar risk_level "LOW | MEDIUM | HIGH"
        float ela_anomaly_score
        varchar metadata_software_detected
        json detected_anomalies
        text explanation
        varchar ela_artifact_path
        timestamp created_at
    }

    VERIFICATION_RESULTS {
        uuid id PK
        uuid user_application_id FK UK
        varchar overall_status "COMPLETE | INCOMPLETE | REVIEW_REQUIRED"
        json satisfied_requirements
        json missing_requirements
        json expired_documents
        json expiring_soon_documents
        json detected_mismatches
        json tampering_flags
        json recommended_actions
        varchar report_pdf_path
        timestamp evaluated_at
    }

    ADMIN_REVIEWS {
        uuid id PK
        uuid user_application_id FK
        uuid admin_user_id FK
        varchar previous_status
        varchar new_status
        text review_notes
        timestamp created_at
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        varchar action
        varchar entity_type
        varchar entity_id
        varchar ip_address
        json details
        timestamp created_at
    }
```

---

## 2. Table Specifications & Constraints

### 2.1 `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key, Default: `uuid4()` | Unique user identifier |
| `email` | VARCHAR(255) | Unique, Indexed, Not Null | Account email address |
| `hashed_password` | VARCHAR(255) | Not Null | Bcrypt salted hash |
| `full_name` | VARCHAR(255) | Not Null | Full legal name of user |
| `role` | VARCHAR(32) | Default `'USER'`, Not Null | `USER`, `ADMIN`, `AUDITOR` |
| `is_active` | BOOLEAN | Default `TRUE`, Not Null | Account active status |
| `created_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Registration timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Last update timestamp |

### 2.2 `application_profiles`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key, Default: `uuid4()` | Unique profile identifier |
| `code` | VARCHAR(64) | Unique, Indexed, Not Null | Machine key (e.g., `PASSPORT_US`, `STUDENT_VISA_UK`) |
| `name` | VARCHAR(255) | Not Null | Human-readable title |
| `jurisdiction` | VARCHAR(64) | Not Null | Jurisdiction code (e.g. `US`, `UK`, `IN`, `GLOBAL`) |
| `category` | VARCHAR(128) | Not Null | Grouping (e.g. `Travel`, `Employment`, `Identity`) |
| `description` | TEXT | Nullable | Detailed description of requirements |
| `is_active` | BOOLEAN | Default `TRUE`, Not Null | Enable or disable application type |
| `created_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Creation timestamp |

### 2.3 `checklist_requirements`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key, Default: `uuid4()` | Unique requirement identifier |
| `application_profile_id` | UUID | FK -> `application_profiles.id`, ON DELETE CASCADE | Profile association |
| `requirement_code` | VARCHAR(64) | Not Null | Identifier (e.g. `PROOF_OF_IDENTITY`) |
| `display_name` | VARCHAR(255) | Not Null | e.g., "Proof of Identity" |
| `description` | TEXT | Nullable | Guidance notes shown to applicant |
| `is_mandatory` | BOOLEAN | Default `TRUE`, Not Null | Whether document is strictly required |
| `accepted_categories` | JSON / TEXT | Not Null | JSON array of accepted doc categories |
| `min_validity_days` | INTEGER | Default `0`, Not Null | Days of remaining validity required |
| `allow_manual_override`| BOOLEAN | Default `TRUE`, Not Null | Whether admin can manually approve |
| `sort_order` | INTEGER | Default `0`, Not Null | UI display sequence |

### 2.4 `user_applications`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key, Default: `uuid4()` | Unique application instance ID |
| `user_id` | UUID | FK -> `users.id`, ON DELETE CASCADE | Submitting user ID |
| `application_profile_id` | UUID | FK -> `application_profiles.id` | Selected requirement profile |
| `reference_number` | VARCHAR(64) | Unique, Indexed, Not Null | Human-readable code e.g. `APP-2026-98124` |
| `status` | VARCHAR(32) | Default `'DRAFT'`, Not Null | Application state |
| `consent_given` | BOOLEAN | Default `FALSE`, Not Null | Applicant data processing consent |
| `consent_timestamp` | TIMESTAMP WITH TIME ZONE | Nullable | Exact time consent was checked |
| `created_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Application start date |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Last modification |

### 2.5 `uploaded_documents`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key, Default: `uuid4()` | Unique document ID |
| `user_application_id` | UUID | FK -> `user_applications.id`, ON DELETE CASCADE | Application bundle relation |
| `user_id` | UUID | FK -> `users.id` | Ownership reference |
| `original_filename` | VARCHAR(255) | Not Null | Name provided at upload |
| `stored_filename` | VARCHAR(255) | Unique, Not Null | UUID-named file on disk |
| `file_path` | VARCHAR(512) | Not Null | Encrypted storage path |
| `file_size_bytes` | INTEGER | Not Null | File size in bytes |
| `mime_type` | VARCHAR(128) | Not Null | Verified MIME type |
| `file_hash_sha256` | VARCHAR(64) | Not Null | SHA-256 integrity hash |
| `is_encrypted` | BOOLEAN | Default `TRUE`, Not Null | AES-256 storage flag |
| `doc_category` | VARCHAR(64) | Default `'UNKNOWN'`, Not Null | Identified or user-selected category |
| `ocr_status` | VARCHAR(32) | Default `'PENDING'`, Not Null | `PENDING`, `SUCCESS`, `FAILED` |
| `ocr_overall_confidence`| FLOAT | Default `0.0`, Not Null | Mean OCR extraction confidence |
| `raw_text` | TEXT | Nullable | Extracted full OCR text |
| `created_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Upload timestamp |

### 2.6 `extracted_fields`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key, Default: `uuid4()` | Field extraction ID |
| `document_id` | UUID | FK -> `uploaded_documents.id`, ON DELETE CASCADE | Source document |
| `field_key` | VARCHAR(64) | Not Null | e.g. `full_name`, `dob`, `doc_number`, `expiry_date` |
| `raw_value` | VARCHAR(512) | Nullable | Exact text parsed from OCR |
| `normalized_value` | VARCHAR(512) | Nullable | Standardized format (e.g. ISO date) |
| `confidence` | FLOAT | Default `0.0`, Not Null | Extraction confidence score `0.0-1.0` |
| `is_user_corrected` | BOOLEAN | Default `FALSE`, Not Null | Whether modified by user |
| `corrected_value` | VARCHAR(512) | Nullable | Corrected value entered by user |
| `notes` | VARCHAR(255) | Nullable | Parsing diagnostics |
| `created_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Extraction timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Correction timestamp |

### 2.7 `tampering_analyses`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key, Default: `uuid4()` | Tampering analysis ID |
| `document_id` | UUID | Unique, FK -> `uploaded_documents.id`, ON DELETE CASCADE | Document relation |
| `is_flagged` | BOOLEAN | Default `FALSE`, Not Null | Whether flagged for human review |
| `risk_level` | VARCHAR(32) | Default `'LOW'`, Not Null | `LOW`, `MEDIUM`, `HIGH` |
| `ela_anomaly_score` | FLOAT | Default `0.0`, Not Null | ELA variance metric |
| `metadata_software_detected` | VARCHAR(255) | Nullable | Detected editing software (e.g. Photoshop) |
| `detected_anomalies` | JSON / TEXT | Default `'[]'`, Not Null | List of specific anomaly tags |
| `explanation` | TEXT | Nullable | Detailed human-readable reasoning |
| `ela_artifact_path` | VARCHAR(512) | Nullable | Rendered difference map image |
| `created_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Timestamp of run |

### 2.8 `verification_results`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key, Default: `uuid4()` | Verification summary ID |
| `user_application_id` | UUID | Unique, FK -> `user_applications.id`, ON DELETE CASCADE | Application bundle |
| `overall_status` | VARCHAR(32) | Not Null | `COMPLETE`, `INCOMPLETE`, `REVIEW_REQUIRED` |
| `satisfied_requirements` | JSON / TEXT | Not Null | Checklist items satisfied |
| `missing_requirements` | JSON / TEXT | Not Null | Checklist items unsatisfied |
| `expired_documents` | JSON / TEXT | Not Null | Documents evaluated as expired |
| `expiring_soon_documents`| JSON / TEXT | Not Null | Documents approaching cutoff |
| `detected_mismatches` | JSON / TEXT | Not Null | Cross-document field discrepancies |
| `tampering_flags` | JSON / TEXT | Not Null | Suspicious document alerts |
| `recommended_actions` | JSON / TEXT | Not Null | Concrete next actions for user |
| `report_pdf_path` | VARCHAR(512) | Nullable | Path to generated official report |
| `evaluated_at` | TIMESTAMP WITH TIME ZONE | Default `utcnow()` | Evaluation timestamp |

---

## 3. Data Integrity & Indexing Strategy
- Indexes on `users(email)`, `user_applications(reference_number, user_id)`, `uploaded_documents(user_application_id)`.
- Foreign key cascading ensures that deleting an application cleanly purges extracted fields, uploaded files, and verification records in compliance with privacy retention policies.
- Full support for PostgreSQL in production and SQLite in local/testing setups.
