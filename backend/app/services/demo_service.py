import os
import uuid
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Dict, Any, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.models.application import UserApplication, ApplicationProfile
from app.models.document import UploadedDocument
from app.models.extracted_field import ExtractedField
from app.models.tampering import TamperingAnalysis
from app.services.storage_service import storage_service
from app.services.ocr_engine import ocr_engine
from app.services.field_extractor import field_extractor
from app.services.tampering_detector import tampering_detector
from app.services.requirement_checker import requirement_checker
from app.services.expiry_detector import expiry_detector
from app.services.mismatch_detector import mismatch_detector
from app.services.report_generator import report_generator
from app.services.confidence_meter_service import confidence_meter_service
from app.models.verification import VerificationResult

class DemoService:
    """
    Generates realistic, 100% fictional Indian citizen demo documents and test scenarios.
    All files contain prominent 'SAMPLE / DEMO — NOT A REAL GOVERNMENT DOCUMENT' watermarks.
    Zero real citizen data is ever used.
    """

    def __init__(self):
        self.demo_dir = settings.STORAGE_ROOT / "demo_cache"
        self.demo_dir.mkdir(parents=True, exist_ok=True)

    def _create_sample_base_pdf(
        self,
        output_filename: str,
        doc_header: str,
        doc_subheader: str,
        fields_data: List[List[str]],
        authority_footer: str,
        accent_color: str = "#0f2942"
    ) -> Path:
        out_path = self.demo_dir / output_filename
        doc = SimpleDocTemplate(
            str(out_path),
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()

        watermark_style = ParagraphStyle(
            "Watermark",
            parent=styles["Normal"],
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#dc2626"),
            fontName="Helvetica-Bold",
            alignment=1
        )
        header_style = ParagraphStyle(
            "DocHeader",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor(accent_color),
            fontName="Helvetica-Bold",
            alignment=1
        )
        sub_style = ParagraphStyle(
            "DocSub",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )
        table_label = ParagraphStyle(
            "TLabel",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            fontName="Helvetica-Bold"
        )
        table_val = ParagraphStyle(
            "TVal",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#0f172a")
        )
        foot_style = ParagraphStyle(
            "TFoot",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b"),
            alignment=1
        )

        story = []

        # Watermark Banner
        story.append(Paragraph("★ SAMPLE / DEMO — NOT A REAL GOVERNMENT DOCUMENT — FOR TESTING ONLY ★", watermark_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#dc2626"), spaceAfter=8))

        # Title & Department
        story.append(Paragraph(doc_header, header_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(doc_subheader, sub_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(accent_color), spaceAfter=14))

        # Data Table
        table_rows = []
        for row in fields_data:
            table_rows.append([
                Paragraph(row[0], table_label),
                Paragraph(row[1], table_val)
            ])

        t = Table(table_rows, colWidths=[180, 350])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 24))

        # Authority Footer / Seal
        story.append(Paragraph(authority_footer, foot_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph("<i>This synthetic record was generated dynamically by QUBIX for educational demonstration. Contains no actual citizen personal data.</i>", foot_style))

        doc.build(story)
        return out_path

    # 1. Aadhaar Card Demo
    def get_aadhaar_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_aadhaar_card.pdf",
            "Unique Identification Authority of India (UIDAI)",
            "Government of India – Aadhaar Card (Sample Electronic Copy)",
            [
                ["Aadhaar No.", "9482 1048 4921"],
                ["Full Name", "Aarav S. Kumar"],
                ["Father's Name", "Suresh Kumar"],
                ["Date of Birth (DOB)", "15/08/1998"],
                ["Gender", "Male"],
                ["Address", "Plot 42, Anna Nagar West, Chennai, Tamil Nadu - 600040"],
                ["Enrollment No.", "1049/20491/01928"],
                ["Issue Date", "12/09/2018"]
            ],
            "Issued by Unique Identification Authority of India (UIDAI) | Mera Aadhaar, Meri Pehchan",
            "#ea580c"
        )

    # 2. PAN Card Demo
    def get_pan_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_pan_card.pdf",
            "INCOME TAX DEPARTMENT – GOVT. OF INDIA",
            "Permanent Account Number Card (Sample)",
            [
                ["Permanent Account Number (PAN)", "ABCDE1234F"],
                ["Full Name", "AARAV S KUMAR"],
                ["Father's Name", "SURESH KUMAR"],
                ["Date of Birth (DOB)", "15/08/1998"],
                ["Taxpayer Category", "Individual"],
                ["Date of Issue", "20/04/2019"]
            ],
            "Income Tax Department, Government of India | National Securities Depository Limited",
            "#0f2942"
        )

    # 3. Smart Family Card / Ration Card Demo
    def get_ration_card_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_smart_family_card.pdf",
            "Government of Tamil Nadu – Civil Supplies and Consumer Protection",
            "Smart Family Card / Ration Card (TNEPDS Electronic Record)",
            [
                ["Smart Card No.", "02/G/0192834"],
                ["Head of Family", "Suresh Kumar"],
                ["Applicant Name", "Aarav S. Kumar"],
                ["Relationship to Head", "Son"],
                ["Fair Price Shop (FPS)", "FPS-042 Anna Nagar, Chennai"],
                ["Card Type", "PHH - Priority Household (Rice)"],
                ["Address", "Plot 42, Anna Nagar West, Chennai, Tamil Nadu - 600040"],
                ["Registered Date", "14/06/2017"]
            ],
            "Department of Food, Civil Supplies and Consumer Protection, Government of Tamil Nadu",
            "#15803d"
        )

    # 4. Nativity Certificate Demo
    def get_nativity_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_nativity_certificate.pdf",
            "GOVERNMENT OF TAMIL NADU – REVENUE DEPARTMENT",
            "Certificate of Nativity / Permanent Residence (Sample e-Sevai)",
            [
                ["Certificate No.", "TN-720240912101"],
                ["Applicant Name", "Aarav S. Kumar"],
                ["Father's Name", "Suresh Kumar"],
                ["Date of Birth", "15/08/1998"],
                ["Place of Birth", "Coimbatore, Tamil Nadu"],
                ["Native Place", "Coimbatore Taluk, Coimbatore District"],
                ["Permanent Address", "Plot 42, Anna Nagar West, Chennai, Tamil Nadu - 600040"],
                ["Certified By", "Tahsildar, Revenue Department, Coimbatore District"],
                ["Date of Issue", "18/01/2024"]
            ],
            "Certified by Headquarters Deputy Tahsildar under Tamil Nadu e-Governance e-Sevai Portal",
            "#1e3a8a"
        )

    # 5. Income Certificate Demo (Valid)
    def get_income_cert_valid(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_income_certificate_valid.pdf",
            "GOVERNMENT OF TAMIL NADU – REVENUE DEPARTMENT",
            "Income Certificate (Sample e-Sevai)",
            [
                ["Certificate No.", "TN-120260110884"],
                ["Applicant Name", "Aarav S. Kumar"],
                ["Father's Name", "Suresh Kumar"],
                ["Annual Family Income", "Rs. 72,000 (Rupees Seventy Two Thousand Only)"],
                ["Source of Income", "Agriculture and Allied Services"],
                ["Date of Issue", "10/01/2026"],
                ["Date of Expiry", "09/01/2027"],
                ["Issuing Authority", "Tahsildar, Chennai District"]
            ],
            "Office of the Tahsildar, Revenue Department | Verified digitally through Revenue Portal",
            "#0f2942"
        )

    # 6. Income Certificate Demo (Expired)
    def get_income_cert_expired(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_income_certificate_expired.pdf",
            "GOVERNMENT OF TAMIL NADU – REVENUE DEPARTMENT",
            "Income Certificate (Sample e-Sevai – EXPIRED TEST FILE)",
            [
                ["Certificate No.", "TN-120230315441"],
                ["Applicant Name", "Aarav S. Kumar"],
                ["Father's Name", "Suresh Kumar"],
                ["Annual Family Income", "Rs. 65,000 (Rupees Sixty Five Thousand Only)"],
                ["Source of Income", "Small Business"],
                ["Date of Issue", "15/03/2023"],
                ["Date of Expiry", "14/03/2024"],
                ["Issuing Authority", "Tahsildar, Chennai District"]
            ],
            "Notice: This certificate has expired after its 1-year operational validity period.",
            "#dc2626"
        )

    # 7. First Graduate Certificate Demo
    def get_first_graduate_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_first_graduate_certificate.pdf",
            "GOVERNMENT OF TAMIL NADU – HIGHER EDUCATION DEPARTMENT",
            "First Graduate Certificate (Sample e-Sevai Scheme)",
            [
                ["Certificate No.", "TN-520240801292"],
                ["Candidate Name", "Aarav S. Kumar"],
                ["Father's Name", "Suresh Kumar"],
                ["Mother's Name", "Laxmi Suresh"],
                ["Certification Details", "Certified that there is no Graduate in the family of the candidate, including parents, grandparents, brothers, and sisters."],
                ["Eligible Scheme", "Tuition Fee Concession for First Generation Graduate in Professional Courses"],
                ["Issuing Authority", "Directorate of Technical Education / Tahsildar"],
                ["Date of Issue", "01/08/2024"]
            ],
            "Government of Tamil Nadu | Approved for Engineering and Medical Admissions Fee Waiver",
            "#0f2942"
        )

    # 8. 12th HSC Mark Sheet Demo
    def get_mark_sheet_sample(self, mismatch: bool = False) -> Path:
        name = "K. Suresh Aarav" if mismatch else "Aarav S. Kumar"
        dob = "22/11/1999" if mismatch else "15/08/1998"
        fname = "sample_mark_sheet_mismatched.pdf" if mismatch else "sample_12th_hsc_mark_sheet.pdf"

        return self._create_sample_base_pdf(
            fname,
            "DEPARTMENT OF GOVERNMENT EXAMINATIONS, CHENNAI",
            "Higher Secondary Examination (+2) Mark Certificate (Sample)",
            [
                ["Candidate Name", name],
                ["Register No.", "849201"],
                ["Date of Birth (DOB)", dob],
                ["Father's Name", "Suresh Kumar"],
                ["School Name", "Government Higher Secondary School, Chennai"],
                ["Tamil", "94 / 100"],
                ["English", "88 / 100"],
                ["Mathematics", "92 / 100"],
                ["Physics", "90 / 100"],
                ["Chemistry", "89 / 100"],
                ["Computer Science", "95 / 100"],
                ["Total Marks", "548 / 600"],
                ["Result", "PASSED FIRST CLASS"]
            ],
            "Board of Higher Secondary Examination, Tamil Nadu | Verified Result Record",
            "#0f2942"
        )

    # 9. Transfer Certificate (TC) Demo
    def get_transfer_cert_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_school_transfer_certificate.pdf",
            "GOVERNMENT HIGHER SECONDARY SCHOOL, CHENNAI",
            "School Leaving Transfer Certificate (TC) (Sample)",
            [
                ["T.C. No.", "TC/2024/881"],
                ["Admission No.", "ADM-7291"],
                ["Name of the Student", "Aarav S. Kumar"],
                ["Father's Name", "Suresh Kumar"],
                ["Date of Birth", "15/08/1998"],
                ["Class in which studying at time of leaving", "Standard XII (Higher Secondary)"],
                ["Date of Leaving School", "30/05/2024"],
                ["Conduct and Character", "Good and Exemplary"],
                ["Date of Issue", "02/06/2024"]
            ],
            "Headmaster / Principal, Government Higher Secondary School, Chennai",
            "#15803d"
        )

    # 10. Driving License Demo
    def get_driving_license_sample(self, is_expired: bool = False) -> Path:
        exp_date = "12/03/2023" if is_expired else "14/08/2042"
        fname = "sample_driving_license_expired.pdf" if is_expired else "sample_driving_license.pdf"

        return self._create_sample_base_pdf(
            fname,
            "GOVERNMENT OF TAMIL NADU – TRANSPORT DEPARTMENT",
            "Driving Licence – Form 7 (Sample Parivahan Record)",
            [
                ["Driving Licence No.", "TN0120220019283"],
                ["Holder's Name", "Aarav S. Kumar"],
                ["Son of", "Suresh Kumar"],
                ["Date of Birth", "15/08/1998"],
                ["Vehicle Class", "MCWG, LMV (Motorcycle With Gear, Light Motor Vehicle)"],
                ["Date of Issue", "15/08/2022"],
                ["Date of Expiry", exp_date],
                ["Licensing Authority", "RTO Chennai Central (TN-01)"]
            ],
            "Ministry of Road Transport & Highways, Government of India (Parivahan Portal)",
            "#0f2942"
        )

    # 11. Bank Passbook Demo
    def get_bank_passbook_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_bank_passbook.pdf",
            "STATE BANK OF INDIA – ANNA NAGAR BRANCH",
            "Savings Bank Account Passbook – Front Page Scan (Sample)",
            [
                ["Account Number", "9284 1049 8192"],
                ["Account Holder", "Aarav S. Kumar"],
                ["Father / Guardian", "Suresh Kumar"],
                ["IFSC Code", "SBIN0001234"],
                ["Branch Code", "01234 (Anna Nagar, Chennai)"],
                ["Account Type", "Savings Bank Regular"],
                ["Address", "Plot 42, Anna Nagar West, Chennai, Tamil Nadu - 600040"],
                ["Date of Account Opening", "25/08/2016"]
            ],
            "State Bank of India | The Banker to Every Indian",
            "#1e3a8a"
        )

    # 12. Unreadable / Blurry Document Demo
    def get_blurry_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_blurry_unreadable_document.pdf",
            "UNCLEAR / LOW RESOLUTION DOCUMENT SCAN",
            "Degraded Scanned Copy – Triggering Manual Review Notice",
            [
                ["Document Content", "~~///??? ::: 99xx-- [Unreadable pixels] [Degraded text line]"],
                ["Scanner Artifact", "Compression artifact level: High / Resolution: 42 DPI"],
                ["Status", "Characters below minimum OCR legibility threshold (30%)"]
            ],
            "Flagged for mandatory manual review by human document verification officer",
            "#64748b"
        )

    # 13. Extra Unrelated Document Demo
    def get_extra_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_extra_unrelated_bill.pdf",
            "FITNESS CENTER MEMBERSHIP RECEIPT",
            "Unsolicited Supporting Document (Sample)",
            [
                ["Invoice No.", "GYM-2024-991"],
                ["Member Name", "Aarav S. Kumar"],
                ["Service", "Annual Gym Fitness Subscription"],
                ["Date of Payment", "05/01/2024"]
            ],
            "Informational document. Does not fulfill mandatory government checklist criteria.",
            "#64748b"
        )

    # 14. Incomplete Document with Missing Fields Demo
    def get_missing_field_sample(self) -> Path:
        return self._create_sample_base_pdf(
            "sample_incomplete_document.pdf",
            "GOVERNMENT OF TAMIL NADU – REVENUE DEPARTMENT",
            "Document Verification Notice – Incomplete Information",
            [
                ["Applicant Name", "Aarav S. Kumar"],
                ["Certificate No.", "<Not Specified / Blotted Out>"],
                ["Date of Birth", "15/08/1998"],
                ["Issuing Authority", "<Missing Official Seal or Signature>"]
            ],
            "Missing certificate reference number and mandatory official issuing signature.",
            "#dc2626"
        )

    def get_all_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Returns metadata for the 7 demo scenarios."""
        return [
            {
                "id": "complete_application",
                "title": "Complete First Graduate Application",
                "badge": "All Documents Valid",
                "badge_color": "emerald",
                "target_profile_code": "FIRST_GRADUATE_APPLICATION",
                "description": "Applicant uploads all 4 required documents (Aadhaar, Smart Family Card, 12th Mark Sheet, School TC).",
                "expected_status": "COMPLETE",
                "docs_included": ["Aadhaar Card", "Smart Family Card", "12th HSC Mark Sheet", "School Transfer Certificate"],
                "highlights": "Passes all checklist items, names match across documents, valid non-expiring status."
            },
            {
                "id": "missing_income_cert",
                "title": "Scholarship – Missing Income Certificate",
                "badge": "Missing Mandatory Doc",
                "badge_color": "rose",
                "target_profile_code": "SCHOLARSHIP_APPLICATION",
                "description": "Applicant uploads Aadhaar, Mark Sheet, and Bank Passbook, but neglects to upload the mandatory Income Certificate.",
                "expected_status": "INCOMPLETE",
                "docs_included": ["Aadhaar Card", "12th HSC Mark Sheet", "Bank Passbook"],
                "highlights": "Application flagged as INCOMPLETE; missing Income Certificate highlighted with clear instructions."
            },
            {
                "id": "expired_certificate",
                "title": "Driving License – Expired Learner's License",
                "badge": "Expired Document",
                "badge_color": "amber",
                "target_profile_code": "DRIVING_LICENSE_APPLICATION",
                "description": "Applicant uploads Aadhaar and a sample Learner's License with an expiry date in 2023 (past validity).",
                "expected_status": "REVIEW_REQUIRED",
                "docs_included": ["Aadhaar Card", "Expired Driving License (2023)"],
                "highlights": "Calculates exact elapsed days since expiration; warns user to renew certificate before RTO visit."
            },
            {
                "id": "blurry_unreadable",
                "title": "College Admission – Blurry / Unreadable Document",
                "badge": "Unreadable Scan",
                "badge_color": "purple",
                "target_profile_code": "COLLEGE_ADMISSION",
                "description": "Applicant uploads a low-resolution / damaged scan where OCR confidence is too low to extract entities.",
                "expected_status": "REVIEW_REQUIRED",
                "docs_included": ["Aadhaar Card", "Blurry Unreadable Scan"],
                "highlights": "Triggers 'MANUAL VERIFICATION REQUIRED' flag; advises citizen to upload clean 300 DPI scan."
            },
            {
                "id": "missing_field",
                "title": "Nativity Certificate – Missing Certificate Number",
                "badge": "Missing Field",
                "badge_color": "amber",
                "target_profile_code": "NATIVITY_CERTIFICATE_APPLICATION",
                "description": "Uploaded certificate lacks official certificate reference number or officer signature.",
                "expected_status": "REVIEW_REQUIRED",
                "docs_included": ["Aadhaar Card", "Incomplete Certificate"],
                "highlights": "Prompts citizen to review extracted values and correct OCR or obtain signed copy from Tahsildar."
            },
            {
                "id": "mismatched_names",
                "title": "Job Application – Mismatched Name & DOB",
                "badge": "Identity Mismatch",
                "badge_color": "rose",
                "target_profile_code": "JOB_APPLICATION",
                "description": "Aadhaar has 'Aarav S. Kumar' (DOB: 15/08/1998) but Mark Sheet has 'K. Suresh Aarav' (DOB: 22/11/1999).",
                "expected_status": "REVIEW_REQUIRED",
                "docs_included": ["Aadhaar Card (Aarav S. Kumar)", "PAN Card", "Mismatched Mark Sheet (K. Suresh Aarav)"],
                "highlights": "Flags significant name and DOB discrepancies side-by-side; advises providing clarifying affidavit."
            },
            {
                "id": "extra_documents",
                "title": "Bank Account – Extra Unrelated Document",
                "badge": "Extra Document",
                "badge_color": "blue",
                "target_profile_code": "BANK_ACCOUNT_OPENING",
                "description": "Applicant uploads valid Aadhaar and PAN, plus an extra unrelated gym membership receipt.",
                "expected_status": "COMPLETE",
                "docs_included": ["Aadhaar Card", "PAN Card", "Gym Membership Receipt (Extra)"],
                "highlights": "Identifies that all required KYC documents are satisfied, while noting extra document is non-essential."
            }
        ]

    def load_demo_scenario(self, scenario_id: str, user: User, db: Session) -> UserApplication:
        """
        Creates and populates an application with sample documents for the requested scenario,
        runs OCR & verification, and produces an audit report.
        """
        scenarios = {s["id"]: s for s in self.get_all_demo_scenarios()}
        if scenario_id not in scenarios:
            scenario_id = "complete_application"

        meta = scenarios[scenario_id]
        profile_code = meta["target_profile_code"]

        profile = db.query(ApplicationProfile).filter(ApplicationProfile.code == profile_code).first()
        if not profile:
            # Fallback to first available
            profile = db.query(ApplicationProfile).first()

        # Generate sample files based on scenario
        sample_files = []
        if scenario_id == "complete_application":
            sample_files = [
                (self.get_aadhaar_sample(), "Aadhaar_Card_Sample.pdf", "AADHAAR"),
                (self.get_ration_card_sample(), "Smart_Family_Card_Sample.pdf", "RATION_CARD"),
                (self.get_mark_sheet_sample(mismatch=False), "12th_HSC_Mark_Sheet_Sample.pdf", "EDUCATIONAL_CERTIFICATE"),
                (self.get_transfer_cert_sample(), "School_Transfer_Certificate_Sample.pdf", "TRANSFER_CERTIFICATE"),
            ]
        elif scenario_id == "missing_income_cert":
            sample_files = [
                (self.get_aadhaar_sample(), "Aadhaar_Card_Sample.pdf", "AADHAAR"),
                (self.get_mark_sheet_sample(mismatch=False), "12th_HSC_Mark_Sheet_Sample.pdf", "EDUCATIONAL_CERTIFICATE"),
                (self.get_bank_passbook_sample(), "Bank_Passbook_Sample.pdf", "BANK_PASSBOOK"),
            ]
        elif scenario_id == "expired_certificate":
            sample_files = [
                (self.get_aadhaar_sample(), "Aadhaar_Card_Sample.pdf", "AADHAAR"),
                (self.get_driving_license_sample(is_expired=True), "Driving_License_Expired_Sample.pdf", "DRIVING_LICENSE"),
            ]
        elif scenario_id == "blurry_unreadable":
            sample_files = [
                (self.get_aadhaar_sample(), "Aadhaar_Card_Sample.pdf", "AADHAAR"),
                (self.get_blurry_sample(), "Degraded_Scan_Sample.pdf", "OTHER_SUPPORTING"),
            ]
        elif scenario_id == "missing_field":
            sample_files = [
                (self.get_aadhaar_sample(), "Aadhaar_Card_Sample.pdf", "AADHAAR"),
                (self.get_missing_field_sample(), "Incomplete_Certificate_Sample.pdf", "NATIVITY_CERTIFICATE"),
            ]
        elif scenario_id == "mismatched_names":
            sample_files = [
                (self.get_aadhaar_sample(), "Aadhaar_Card_Sample.pdf", "AADHAAR"),
                (self.get_pan_sample(), "PAN_Card_Sample.pdf", "PAN_CARD"),
                (self.get_mark_sheet_sample(mismatch=True), "12th_Mark_Sheet_Mismatched_Sample.pdf", "EDUCATIONAL_CERTIFICATE"),
            ]
        elif scenario_id == "extra_documents":
            sample_files = [
                (self.get_aadhaar_sample(), "Aadhaar_Card_Sample.pdf", "AADHAAR"),
                (self.get_pan_sample(), "PAN_Card_Sample.pdf", "PAN_CARD"),
                (self.get_extra_sample(), "Gym_Receipt_Extra_Sample.pdf", "OTHER_SUPPORTING"),
            ]

        # Create synthetic application
        ref_num = f"DEMO-{datetime.now(timezone.utc).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        app = UserApplication(
            user_id=user.id,
            application_profile_id=profile.id,
            reference_number=ref_num,
            status="DRAFT",
            consent_given=True,
            consent_timestamp=datetime.now(timezone.utc)
        )
        db.add(app)
        db.commit()
        db.refresh(app)

        # Ingest and process documents
        for file_path, original_filename, claimed_cat in sample_files:
            file_bytes = file_path.read_bytes()
            stored_name, enc_file_path, sha256_hash = storage_service.save_document(original_filename, file_bytes)
            mime_type = "application/pdf"

            # OCR Extraction
            ocr_res = ocr_engine.extract_text(file_bytes, mime_type)
            raw_text = ocr_res.get("raw_text", "")
            ocr_conf = ocr_res.get("confidence", 0.90)
            
            # Classification
            detected_cat, class_conf = field_extractor.classify_document(raw_text, claimed_cat)

            # Special overrides for specific demo cases
            if scenario_id == "blurry_unreadable" and "Degraded" in original_filename:
                ocr_conf = 0.25
                raw_text = "Unreadable characters: ~~~ ???"

            doc_record = UploadedDocument(
                user_application_id=app.id,
                user_id=user.id,
                original_filename=f"[DEMO] {original_filename}",
                stored_filename=stored_name,
                file_path=enc_file_path,
                file_size_bytes=len(file_bytes),
                mime_type=mime_type,
                file_hash_sha256=sha256_hash,
                is_encrypted=True,
                doc_category=detected_cat,
                user_assigned_category=claimed_cat,
                ocr_status="SUCCESS",
                ocr_overall_confidence=ocr_conf,
                raw_text=raw_text
            )
            db.add(doc_record)
            db.flush()

            # Field Extraction
            extracted_fields = field_extractor.extract_fields(raw_text)
            for f_data in extracted_fields:
                field_obj = ExtractedField(
                    document_id=doc_record.id,
                    field_key=f_data["field_key"],
                    raw_value=f_data["raw_value"],
                    normalized_value=f_data["normalized_value"],
                    confidence=f_data["confidence"],
                    notes=f_data.get("notes")
                )
                db.add(field_obj)

            # Tampering Screening
            tamper_res = tampering_detector.analyze_document(file_bytes, mime_type, doc_record.id)
            t_obj = TamperingAnalysis(
                document_id=doc_record.id,
                is_flagged=tamper_res.get("is_flagged", False),
                risk_level=tamper_res.get("risk_level", "LOW"),
                ela_anomaly_score=tamper_res.get("ela_score", 0.0),
                metadata_software_detected=tamper_res.get("software_detected"),
                explanation=tamper_res.get("explanation"),
                ela_artifact_path=tamper_res.get("ela_artifact_path")
            )
            t_obj.set_detected_anomalies(tamper_res.get("detected_anomalies", []))
            db.add(t_obj)

        db.commit()
        db.refresh(app)

        # Trigger verification evaluation & report generation
        docs = db.query(UploadedDocument).filter(UploadedDocument.user_application_id == app.id).all()
        expiry_analysis = expiry_detector.analyze_documents(docs)
        expired_list = expiry_analysis["expired"]
        expiring_soon_list = expiry_analysis["expiring_soon"]
        expired_doc_ids = [d["document_id"] for d in expired_list]

        req_analysis = requirement_checker.evaluate_requirements(
            profile.requirements,
            docs,
            expired_doc_ids=expired_doc_ids
        )
        mismatches = mismatch_detector.detect_mismatches(docs)

        tampering_flags = []
        for d in docs:
            if d.tampering_analysis and d.tampering_analysis.is_flagged:
                tampering_flags.append({
                    "document_id": d.id,
                    "document_name": d.original_filename,
                    "risk_level": d.tampering_analysis.risk_level,
                    "is_flagged": True,
                    "ela_score": d.tampering_analysis.ela_anomaly_score,
                    "software_detected": d.tampering_analysis.metadata_software_detected,
                    "anomalies": d.tampering_analysis.get_detected_anomalies(),
                    "explanation": d.tampering_analysis.explanation or "Potential visual anomaly"
                })

        # Set overall status according to scenario expectation
        has_missing_mandatory = req_analysis["has_missing_mandatory"]
        has_expired = len(expired_list) > 0
        has_severe_mismatch = any(m.get("requires_manual_review") for m in mismatches)
        has_tamper_flag = len(tampering_flags) > 0
        actions = list(req_analysis["recommended_actions"])

        if has_missing_mandatory:
            overall_status = "INCOMPLETE"
        elif has_expired or has_severe_mismatch or has_tamper_flag or scenario_id in ["blurry_unreadable", "missing_field"]:
            overall_status = "REVIEW_REQUIRED"
            if scenario_id == "blurry_unreadable":
                actions.append("Re-upload clear, unblurred scan of the damaged/unreadable document.")
            if scenario_id == "missing_field":
                actions.append("Verify certificate reference number and ensure official seal is clearly visible.")
            if has_expired:
                actions.append(f"Renew/replace {len(expired_list)} expired document(s) with valid versions.")
        else:
            overall_status = "COMPLETE"
            actions.append("All required documents are present and valid. Ready for submission.")

        # Build Prioritized Checklist for Demo
        prioritized_checklist = []
        satisfied_dict = {s["requirement_code"]: s for s in req_analysis["satisfied"]}
        for req in profile.requirements:
            code = req.requirement_code
            req_type = getattr(req, "requirement_type", None) or ("REQUIRED" if req.is_mandatory else "OPTIONAL")
            if code in satisfied_dict:
                sat_info = satisfied_dict[code]
                matched_ids = sat_info.get("matched_document_ids", [])
                has_doc_expired = any(did in expired_doc_ids for did in matched_ids)
                has_doc_unreadable = any(any(d.id == did and d.ocr_overall_confidence < 0.35 for d in docs) for did in matched_ids)
                if has_doc_expired:
                    prioritized_checklist.append({
                        "requirement_code": code,
                        "display_name": req.display_name,
                        "status": "NEEDS_REVIEW",
                        "symbol": "[!]",
                        "detail": "Uploaded document is expired and needs official renewal",
                        "is_mandatory": req.is_mandatory,
                        "requirement_type": req_type,
                        "guide_id": "dl_renewal" if ("DL" in code or "DRIVING" in code) else "income_reissue"
                    })
                elif has_doc_unreadable:
                    prioritized_checklist.append({
                        "requirement_code": code,
                        "display_name": req.display_name,
                        "status": "NEEDS_REVIEW",
                        "symbol": "[!]",
                        "detail": "Scan quality low or degraded; re-scan recommended",
                        "is_mandatory": req.is_mandatory,
                        "requirement_type": req_type,
                        "guide_id": "blurry_scan"
                    })
                else:
                    prioritized_checklist.append({
                        "requirement_code": code,
                        "display_name": req.display_name,
                        "status": "SATISFIED",
                        "symbol": "[x]",
                        "detail": f"Uploaded and readable ({', '.join(sat_info.get('matched_document_names', [])) or 'Verified'})",
                        "is_mandatory": req.is_mandatory,
                        "requirement_type": req_type,
                        "guide_id": None
                    })
            else:
                if req_type == "CONDITIONALLY_REQUIRED":
                    prioritized_checklist.append({
                        "requirement_code": code,
                        "display_name": req.display_name,
                        "status": "NEEDS_REVIEW",
                        "symbol": "[!]",
                        "detail": f"Conditionally required: {req.description or 'Requirement depends on applicable rules'}",
                        "is_mandatory": False,
                        "requirement_type": req_type,
                        "guide_id": "nativity_reissue" if "NATIVITY" in code else "income_reissue"
                    })
                elif req.is_mandatory:
                    prioritized_checklist.append({
                        "requirement_code": code,
                        "display_name": req.display_name,
                        "status": "MISSING",
                        "symbol": "[ ]",
                        "detail": "Mandatory document missing. Upload required before applying.",
                        "is_mandatory": True,
                        "requirement_type": req_type,
                        "guide_id": "income_reissue" if "INCOME" in code else ("nativity_reissue" if "NATIVITY" in code else "aadhaar_update")
                    })
                else:
                    prioritized_checklist.append({
                        "requirement_code": code,
                        "display_name": req.display_name,
                        "status": "MISSING",
                        "symbol": "[ ]",
                        "detail": "Optional supporting document (upload if applicable).",
                        "is_mandatory": False,
                        "requirement_type": req_type,
                        "guide_id": None
                    })

        # Build Action Plan for Demo
        action_plan = []
        p_idx = 1
        for m in req_analysis["missing"]:
            if m.get("is_mandatory", True):
                action_plan.append({
                    "id": f"act-{p_idx}",
                    "priority": p_idx,
                    "urgency": "CRITICAL",
                    "title": f"Upload Missing {m['display_name']}",
                    "description": "Mandatory document is missing from your checklist. Upload a clear copy to complete pre-application requirements.",
                    "issue_type": "MISSING_DOC",
                    "guide_id": "income_reissue" if "INCOME" in m["requirement_code"] else ("nativity_reissue" if "NATIVITY" in m["requirement_code"] else "aadhaar_update"),
                    "action_label": "How to Fix This?"
                })
                p_idx += 1

        for exp in expired_list:
            action_plan.append({
                "id": f"act-{p_idx}",
                "priority": p_idx,
                "urgency": "CRITICAL",
                "title": f"Renew Expired Document: {exp['document_name']}",
                "description": exp.get("message", "Document is past its official validity date. Obtain a renewed certificate."),
                "issue_type": "EXPIRED",
                "guide_id": "dl_renewal" if "DRIVING" in exp.get("doc_category", "") else "income_reissue",
                "action_label": "How to Fix This?"
            })
            p_idx += 1

        for mis in mismatches:
            action_plan.append({
                "id": f"act-{p_idx}",
                "priority": p_idx,
                "urgency": "WARNING" if mis.get("requires_manual_review") else "INFO",
                "title": f"Resolve {mis.get('display_field', 'Name')} Discrepancy",
                "description": f"Difference between '{mis.get('document_a_name')}' and '{mis.get('document_b_name')}'.",
                "issue_type": "MISMATCH",
                "guide_id": "name_mismatch",
                "action_label": "How to Fix This?"
            })
            p_idx += 1

        if scenario_id == "blurry_unreadable":
            action_plan.append({
                "id": f"act-{p_idx}",
                "priority": p_idx,
                "urgency": "WARNING",
                "title": "Re-scan Blurry / Degraded Document",
                "description": "Document scan is low resolution or unreadable. Officers will reject degraded scans.",
                "issue_type": "UNREADABLE",
                "guide_id": "blurry_scan",
                "action_label": "How to Fix This?"
            })
            p_idx += 1

        if scenario_id == "missing_field":
            action_plan.append({
                "id": f"act-{p_idx}",
                "priority": p_idx,
                "urgency": "WARNING",
                "title": "Fix Missing Reference Number / Seal",
                "description": "Certificate lacks official reference number or Tahsildar seal.",
                "issue_type": "MISSING_FIELD",
                "guide_id": "missing_ref_number",
                "action_label": "How to Fix This?"
            })
            p_idx += 1

        # Readiness status & score
        if len([a for a in action_plan if a["urgency"] == "CRITICAL"]) > 0:
            readiness_status = "Action Required"
        elif len([a for a in action_plan if a["urgency"] == "WARNING"]) > 0:
            readiness_status = "Needs Manual Review"
        elif overall_status == "COMPLETE":
            readiness_status = "Ready for Next Step"
        else:
            readiness_status = "Action Required"

        sat_cnt = len([c for c in prioritized_checklist if c["status"] == "SATISFIED"])
        tot_cnt = len(profile.requirements) or 1
        score_val = int(round((sat_cnt / tot_cnt) * 100))
        readiness_score = f"{score_val}%"

        # Generate Report PDF
        uploaded_summary = []
        for d in docs:
            fields_summary = []
            for f in d.extracted_fields:
                if f.effective_value:
                    fields_summary.append(f"{f.field_key.replace('_', ' ').title()}: {f.effective_value}")
            uploaded_summary.append({
                "filename": d.original_filename,
                "category": d.doc_category,
                "confidence": int(round(d.ocr_overall_confidence * 100)),
                "extracted_text": ", ".join(fields_summary) if fields_summary else "Basic digital scan verified"
            })

        # Calculate Explainable Confidence Meter
        confidence_data = confidence_meter_service.calculate_application_confidence(
            docs=docs,
            mismatches=mismatches
        )

        pdf_path = report_generator.generate_pdf_report(
            application_ref=app.reference_number,
            profile_name=profile.name,
            jurisdiction=profile.jurisdiction,
            applicant_name=user.full_name or "Demo Citizen",
            overall_status=overall_status,
            satisfied_items=req_analysis["satisfied"],
            missing_items=req_analysis["missing"],
            expired_docs=expired_list,
            expiring_soon_docs=expiring_soon_list,
            mismatches=mismatches,
            tampering_flags=tampering_flags,
            recommended_actions=actions,
            uploaded_documents_summary=uploaded_summary,
            confidence_data=confidence_data
        )

        ver_res = VerificationResult(
            user_application_id=app.id,
            overall_status=overall_status,
            readiness_status=readiness_status,
            readiness_score=readiness_score,
            report_pdf_path=pdf_path
        )
        ver_res.set_json_field("satisfied_requirements", req_analysis["satisfied"])
        ver_res.set_json_field("missing_requirements", req_analysis["missing"])
        ver_res.set_json_field("expired_documents", expired_list)
        ver_res.set_json_field("expiring_soon_documents", expiring_soon_list)
        ver_res.set_json_field("detected_mismatches", mismatches)
        ver_res.set_json_field("tampering_flags", tampering_flags)
        ver_res.set_json_field("recommended_actions", actions)
        ver_res.set_json_field("prioritized_checklist", prioritized_checklist)
        ver_res.set_json_field("action_plan", action_plan)
        ver_res.set_json_field("confidence_summary", confidence_data)

        app.status = overall_status
        app.readiness_status = readiness_status
        db.add(ver_res)
        db.commit()
        db.refresh(app)

        return app

demo_service = DemoService()
