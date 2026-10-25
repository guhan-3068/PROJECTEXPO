import os
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, Image as RLImage
from app.config import settings

def _safe(text: Any) -> str:
    """Escapes XML entities so ReportLab Paragraph never crashes on special chars."""
    if text is None:
        return ""
    return escape(str(text))

class ReportGenerator:
    """
    Generates professional verification audit reports in PDF format
    tailored for Indian Citizen Services & General Verification.
    """

    def generate_pdf_report(
        self,
        application_ref: str,
        profile_name: str,
        jurisdiction: str,
        applicant_name: str,
        overall_status: str,
        satisfied_items: list,
        missing_items: list,
        expired_docs: list,
        expiring_soon_docs: list,
        mismatches: list,
        tampering_flags: list,
        recommended_actions: list,
        uploaded_documents_summary: list = None,
        confidence_data: dict = None,
        regulatory_advisories: list = None
    ) -> str:
        report_filename = f"verification_report_{application_ref}_{uuid.uuid4().hex[:6]}.pdf"
        output_path = settings.STORAGE_ROOT / "reports" / report_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f2942"),  # Indian Navy
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#475569")
        )
        badge_style = ParagraphStyle(
            "BadgeText",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            fontName="Helvetica-Bold",
            alignment=1
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0f2942"),
            fontName="Helvetica-Bold",
            spaceBefore=8,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#334155")
        )
        body_bold = ParagraphStyle(
            "ReportBodyBold",
            parent=body_style,
            fontName="Helvetica-Bold"
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=11,
            textColor=colors.HexColor("#64748b"),
            fontName="Helvetica-Oblique"
        )

        story = []

        # Current time in IST (UTC + 5:30)
        ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        formatted_date = ist_time.strftime("%d-%b-%Y %I:%M %p IST")

        # 1. Header Banner with Official QUBIX Logo
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "qubix-logo.png"
        has_logo = logo_path.exists()

        if has_logo:
            logo_img = RLImage(str(logo_path), width=44, height=44)
            header_table_data = [
                [
                    logo_img,
                    Paragraph("<b>QUBIX</b> - Smart Document Verification System", title_style),
                    Paragraph(f"<font color='#0f2942'><b>AUDIT REPORT</b></font><br/><font color='#64748b'>{_safe(application_ref)}</font>", subtitle_style)
                ],
                [
                    "",
                    Paragraph("Government of India / State e-Governance Document Readiness Assistant", subtitle_style),
                    Paragraph(f"Generated: {_safe(formatted_date)}", subtitle_style)
                ]
            ]
            header_table = Table(header_table_data, colWidths=[50, 310, 180])
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("SPAN", (0, 0), (0, 1)),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]))
        else:
            header_table_data = [
                [
                    Paragraph("<b>QUBIX</b> - Smart Document Verification System", title_style),
                    Paragraph(f"<font color='#0f2942'><b>AUDIT REPORT</b></font><br/><font color='#64748b'>{_safe(application_ref)}</font>", subtitle_style)
                ],
                [
                    Paragraph("Government of India / State e-Governance Document Readiness Assistant", subtitle_style),
                    Paragraph(f"Generated: {_safe(formatted_date)}", subtitle_style)
                ]
            ]
            header_table = Table(header_table_data, colWidths=[360, 180])
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]))
        story.append(header_table)
        story.append(Spacer(1, 6))

        # Tri-color accent bar: Saffron (#ea580c), White/Navy, Green (#16a34a)
        tri_bar = Table([["", "", ""]], colWidths=[180, 180, 180], rowHeights=[3])
        tri_bar.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#ea580c")),  # Saffron
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#0f2942")),  # Navy
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#16a34a")),  # Green
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(tri_bar)
        story.append(Spacer(1, 8))

        # 2. Executive Summary Block
        if overall_status == "COMPLETE":
            status_text = "<font color='#15803d'><b>COMPLETE (READY TO APPLY)</b></font>"
            status_bg = "#dcfce7"
        elif overall_status == "INCOMPLETE":
            status_text = "<font color='#b91c1c'><b>INCOMPLETE (DOCUMENTS MISSING)</b></font>"
            status_bg = "#fee2e2"
        else:
            status_text = "<font color='#b45309'><b>REVIEW REQUIRED</b></font>"
            status_bg = "#fef3c7"

        summary_data = [
            [
                Paragraph("<b>Applicant Name:</b>", body_style),
                Paragraph(_safe(applicant_name or "Applicant"), body_style),
                Paragraph("<b>Overall Status:</b>", body_style),
                Paragraph(status_text, body_style)
            ],
            [
                Paragraph("<b>Application Category:</b>", body_style),
                Paragraph(_safe(profile_name), body_style),
                Paragraph("<b>Jurisdiction:</b>", body_style),
                Paragraph(_safe(jurisdiction), body_style)
            ],
            [
                Paragraph("<b>Application Reference:</b>", body_style),
                Paragraph(_safe(application_ref), body_style),
                Paragraph("<b>Official Verification:</b>", body_style),
                Paragraph("<font color='#64748b'>Advisory Check (Not Official Clearance)</font>", body_style)
            ]
        ]
        summary_table = Table(summary_data, colWidths=[110, 160, 110, 160])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10))

        # 3. Document Checklist Requirements Matrix
        story.append(Paragraph("1. Document Checklist & Readiness Matrix", section_style))
        checklist_rows = [
            [
                Paragraph("<b>Requirement Name</b>", body_bold),
                Paragraph("<b>Classification</b>", body_bold),
                Paragraph("<b>Status</b>", body_bold),
                Paragraph("<b>Uploaded Document / Diagnostic Details</b>", body_bold)
            ]
        ]
        for item in satisfied_items:
            req_type = item.get("requirement_type", "REQUIRED" if item.get("is_mandatory") else "OPTIONAL")
            type_label = "Required" if req_type == "REQUIRED" else ("Cond. Required" if req_type == "CONDITIONALLY_REQUIRED" else "Optional")
            checklist_rows.append([
                Paragraph(_safe(item.get("display_name", "")), body_style),
                Paragraph(type_label, body_style),
                Paragraph("<font color='#16a34a'><b>SATISFIED</b></font>", body_style),
                Paragraph(_safe(item.get("reason", "Satisfied")), body_style)
            ])
        for item in missing_items:
            req_type = item.get("requirement_type", "REQUIRED" if item.get("is_mandatory") else "OPTIONAL")
            type_label = "Required" if req_type == "REQUIRED" else ("Cond. Required" if req_type == "CONDITIONALLY_REQUIRED" else "Optional")
            checklist_rows.append([
                Paragraph(_safe(item.get("display_name", "")), body_style),
                Paragraph(type_label, body_style),
                Paragraph("<font color='#dc2626'><b>MISSING</b></font>", body_style),
                Paragraph(_safe(item.get("reason", "Not uploaded")), body_style)
            ])

        checklist_table = Table(checklist_rows, colWidths=[150, 75, 75, 240])
        checklist_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(checklist_table)
        story.append(Spacer(1, 10))

        # 4. Uploaded Documents & Extracted OCR Entities
        if uploaded_documents_summary and len(uploaded_documents_summary) > 0:
            story.append(Paragraph("2. Uploaded Documents & Extracted Entities", section_style))
            doc_rows = [
                [
                    Paragraph("<b>Document File</b>", body_bold),
                    Paragraph("<b>Detected Category</b>", body_bold),
                    Paragraph("<b>OCR Match</b>", body_bold),
                    Paragraph("<b>Extracted Values (Masked)</b>", body_bold)
                ]
            ]
            for doc_item in uploaded_documents_summary:
                doc_rows.append([
                    Paragraph(_safe(doc_item.get("filename", "")), body_style),
                    Paragraph(_safe(doc_item.get("category", "").replace("_", " ")), body_style),
                    Paragraph(f"{doc_item.get('confidence', 0)}%", body_style),
                    Paragraph(_safe(doc_item.get("extracted_text", "No entities recognized")), body_style)
                ])
            docs_table = Table(doc_rows, colWidths=[130, 95, 65, 250])
            docs_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(docs_table)
            story.append(Spacer(1, 10))

        # 5. Temporal Validity & Expiry Analysis
        story.append(Paragraph("3. Temporal Validity & Expiry Audit", section_style))
        if expired_docs or expiring_soon_docs:
            expiry_rows = [[
                Paragraph("<b>Document</b>", body_bold),
                Paragraph("<b>Expiry Date</b>", body_bold),
                Paragraph("<b>Status</b>", body_bold),
                Paragraph("<b>Diagnostic Message</b>", body_bold)
            ]]
            for exp in expired_docs:
                expiry_rows.append([
                    Paragraph(_safe(exp.get("document_name", "")), body_style),
                    Paragraph(_safe(str(exp.get("expiry_date", "N/A"))), body_style),
                    Paragraph("<font color='#dc2626'><b>EXPIRED</b></font>", body_style),
                    Paragraph(_safe(exp.get("message", "")), body_style)
                ])
            for exp in expiring_soon_docs:
                expiry_rows.append([
                    Paragraph(_safe(exp.get("document_name", "")), body_style),
                    Paragraph(_safe(str(exp.get("expiry_date", "N/A"))), body_style),
                    Paragraph("<font color='#d97706'><b>EXPIRING SOON</b></font>", body_style),
                    Paragraph(_safe(exp.get("message", "")), body_style)
                ])
            exp_table = Table(expiry_rows, colWidths=[140, 75, 85, 240])
            exp_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fee2e2")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fca5a5")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(exp_table)
        else:
            story.append(Paragraph("[OK] All uploaded documents with detected expiration dates are strictly within their valid operational windows.", body_style))
        story.append(Spacer(1, 10))

        # 6. Cross-Document Information Consistency
        story.append(Paragraph("4. Cross-Document Information Consistency", section_style))
        if mismatches:
            mismatch_rows = [[
                Paragraph("<b>Field</b>", body_bold),
                Paragraph("<b>Document A Value</b>", body_bold),
                Paragraph("<b>Document B Value</b>", body_bold),
                Paragraph("<b>Evaluation / Explanation</b>", body_bold)
            ]]
            for m in mismatches:
                mismatch_rows.append([
                    Paragraph(_safe(m.get("display_field", "")), body_style),
                    Paragraph(f"<b>{_safe(m.get('document_a_name', ''))}:</b> {_safe(m.get('document_a_value', ''))}", body_style),
                    Paragraph(f"<b>{_safe(m.get('document_b_name', ''))}:</b> {_safe(m.get('document_b_value', ''))}", body_style),
                    Paragraph(_safe(m.get("explanation", "")), body_style)
                ])
            mis_table = Table(mismatch_rows, colWidths=[80, 130, 130, 200])
            mis_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fef3c7")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fde68a")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(mis_table)
        else:
            story.append(Paragraph("[OK] No identity discrepancies or conflicting personal names/dates detected across uploaded documents.", body_style))
        story.append(Spacer(1, 10))

        # 7. Document Integrity & Anomaly Screening
        story.append(Paragraph("5. Document Integrity Screening & Advisory Warnings", section_style))
        flagged_tamper = [t for t in (tampering_flags or []) if t.get("is_flagged")]
        if flagged_tamper:
            tamper_rows = [[
                Paragraph("<b>Document</b>", body_bold),
                Paragraph("<b>Screening Status</b>", body_bold),
                Paragraph("<b>Advisory Diagnostic Explanation</b>", body_bold)
            ]]
            for t in flagged_tamper:
                risk_color = "#dc2626" if t.get("risk_level") == "HIGH" else "#d97706"
                tamper_rows.append([
                    Paragraph(_safe(t.get("document_name", "")), body_style),
                    Paragraph(f"<font color='{risk_color}'><b>{_safe(t.get('risk_level', 'REVIEW'))}</b></font>", body_style),
                    Paragraph(_safe(t.get("explanation", "")), body_style)
                ])
            t_table = Table(tamper_rows, colWidths=[140, 90, 310])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fee2e2")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fca5a5")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t_table)
            story.append(Spacer(1, 4))
            story.append(Paragraph("<i>Notice: AI anomaly detections are advisory flags to assist citizens and officers. A document is never deemed fraudulent without official human adjudication.</i>", subtitle_style))
        else:
            story.append(Paragraph("[OK] Document structural analysis completed with standard digital format conformity.", body_style))
        story.append(Spacer(1, 10))

        # 6. Verification Confidence Meter Diagnostics
        story.append(Paragraph("6. Verification Confidence Meter & Explainable Reliability", section_style))
        if confidence_data and "documents" in confidence_data and confidence_data["documents"]:
            conf_rows = [[
                Paragraph("<b>Document</b>", body_bold),
                Paragraph("<b>Overall Reliability</b>", body_bold),
                Paragraph("<b>OCR & Field Quality</b>", body_bold),
                Paragraph("<b>Authenticity Status</b>", body_bold)
            ]]
            for c_doc in confidence_data["documents"]:
                dims = c_doc.get("dimensions", {})
                ocr_d = dims.get("ocr_extraction", {})
                f_d = dims.get("field_completeness", {})
                auth_d = dims.get("official_authenticity", {})
                
                conf_rows.append([
                    Paragraph(_safe(c_doc.get("original_filename", "")), body_style),
                    Paragraph(f"<b>{c_doc.get('overall_score', 0)}%</b> ({_safe(c_doc.get('overall_level', ''))})", body_style),
                    Paragraph(f"OCR: {_safe(ocr_d.get('level', 'N/A'))} | Fields: {f_d.get('score', 0)}%", body_style),
                    Paragraph(f"<font color='#d97706'><b>{_safe(auth_d.get('status', 'Not Verified'))}</b></font>", body_style)
                ])
            conf_table = Table(conf_rows, colWidths=[140, 110, 130, 160])
            conf_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(conf_table)
            story.append(Spacer(1, 4))
            story.append(Paragraph(
                "<i>Official Authenticity Advisory: Confidence metrics measure automated readability, OCR clarity, and cross-consistency. They do not constitute official government approval or authenticity certification from issuing departments.</i>",
                subtitle_style
            ))
        else:
            story.append(Paragraph("[OK] Automated verification readiness screening completed. Official Authenticity: Not Verified (Advisory).", body_style))
        story.append(Spacer(1, 10))

        # 7. Rule Change Radar & Regulatory Advisory
        if regulatory_advisories and len(regulatory_advisories) > 0:
            story.append(Paragraph("7. Rule Change Radar – Active Regulatory Updates", section_style))
            for rad in regulatory_advisories:
                story.append(Paragraph(
                    f"<b>[!] {_safe(rad.get('title', 'Regulatory Update'))}</b> ({_safe(rad.get('source_authority', 'Official Source'))})<br/>"
                    f"<i>Impact:</i> {_safe(rad.get('impact_summary', 'Check latest guidelines.'))}",
                    body_style
                ))
                story.append(Spacer(1, 3))
            story.append(Spacer(1, 6))

        # 8. Actionable Next Steps
        story.append(Paragraph("8. Actionable Next Steps for Citizen", section_style))
        if recommended_actions:
            for act in recommended_actions:
                story.append(Paragraph(f"- {_safe(act)}", body_style))
        else:
            story.append(Paragraph("- No outstanding actions. All required documents are present and ready for official submission.", body_style))

        story.append(Spacer(1, 14))

        # 9. Official Citizen Disclaimer & Footer
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
        story.append(Paragraph(
            "<b>IMPORTANT CITIZEN DISCLAIMER:</b> QUBIX is an independent document-readiness assistance tool. It is not a government website and does not issue, approve, or authenticate government documents. This report does NOT constitute official approval or clearance from UIDAI, Income Tax Department, Transport Department (RTO), or State Revenue authorities. Requirements shown are indicative guidelines. Application approval is never guaranteed, even when every automated check passes.",
            disclaimer_style
        ))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f"QUBIX Citizen Assistant | Confidential Audit Record | Ref: {_safe(application_ref)}",
            subtitle_style
        ))

        doc.build(story)
        return str(output_path)

report_generator = ReportGenerator()
