import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

OUTPUT_DIR = Path(__file__).resolve().parent / "sample_docs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_pdf_passport(filename: str, name: str, dob: str, expiry: str, doc_no: str):
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(str(path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>REPUBLIC OF VERIFICATION - PASSPORT</b>", styles["Heading1"]),
        Spacer(1, 15),
        Paragraph(f"Type: P | Country Code: XAA | Passport No: {doc_no}", styles["Normal"]),
        Spacer(1, 10),
        Paragraph(f"Surname / Given Names: {name}", styles["Normal"]),
        Paragraph(f"Nationality: GLOBAL CITIZEN", styles["Normal"]),
        Paragraph(f"Date of Birth: {dob}", styles["Normal"]),
        Paragraph(f"Sex: M", styles["Normal"]),
        Paragraph(f"Date of Issue: 2020-01-15", styles["Normal"]),
        Paragraph(f"Date of Expiry: {expiry}", styles["Normal"]),
        Paragraph(f"Issuing Authority: PASSPORT AGENCY", styles["Normal"]),
        Spacer(1, 20),
        Paragraph(f"P&lt;XAA{name.upper().replace(' ', '&lt;&lt;')}&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;", styles["Code"]),
        Paragraph(f"{doc_no}&lt;0XAA9005141M3010158&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;02", styles["Code"]),
    ]
    doc.build(story)
    return str(path)

def generate_pdf_utility_bill(filename: str, name: str, address: str):
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(str(path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>METROPOLITAN ELECTRIC & WATER UTILITY BILL</b>", styles["Heading1"]),
        Spacer(1, 15),
        Paragraph(f"Account Number: 8849-2041-92", styles["Normal"]),
        Paragraph(f"Consumer Name: {name}", styles["Normal"]),
        Paragraph(f"Billing Address: {address}", styles["Normal"]),
        Paragraph("Billing Period: 01 Oct 2026 - 31 Oct 2026", styles["Normal"]),
        Paragraph("Statement Total: $142.50", styles["Normal"]),
        Paragraph("Status: PAID IN FULL", styles["Normal"]),
    ]
    doc.build(story)
    return str(path)

def generate_id_image(filename: str, name: str, dob: str, doc_no: str, software_tag: str = None):
    path = OUTPUT_DIR / filename
    img = Image.new("RGB", (600, 360), color=(240, 244, 248))
    draw = ImageDraw.Draw(img)

    # Draw card border and header
    draw.rectangle([10, 10, 590, 350], outline=(51, 65, 85), width=3)
    draw.rectangle([10, 10, 590, 70], fill=(30, 41, 59))
    draw.text((25, 25), "NATIONAL IDENTIFICATION CARD", fill=(255, 255, 255))

    # Details
    draw.text((30, 90), f"Name: {name}", fill=(15, 23, 42))
    draw.text((30, 130), f"Date of Birth: {dob}", fill=(15, 23, 42))
    draw.text((30, 170), f"ID Number: {doc_no}", fill=(15, 23, 42))
    draw.text((30, 210), "Date of Issue: 2022-06-10", fill=(15, 23, 42))
    draw.text((30, 250), "Date of Expiry: 2032-06-10", fill=(15, 23, 42))
    draw.text((30, 290), "Nationality: Citizen", fill=(15, 23, 42))

    # Add photo placeholder box
    draw.rectangle([430, 90, 560, 250], outline=(100, 116, 139), width=2, fill=(226, 232, 240))
    draw.text((450, 160), "[ PHOTO ]", fill=(71, 85, 105))

    png_info = None
    if software_tag:
        from PIL.PngImagePlugin import PngInfo
        png_info = PngInfo()
        png_info.add_text("Software", software_tag)

    if png_info:
        img.save(str(path), "PNG", pnginfo=png_info)
    else:
        img.save(str(path), "PNG")
    return str(path)

if __name__ == "__main__":
    p1 = generate_pdf_passport("passport_valid.pdf", "Alex Taylor", "1990-05-14", "2030-10-15", "P8912401")
    p2 = generate_pdf_passport("passport_expired.pdf", "Alex Taylor", "1990-05-14", "2021-04-10", "P5510928")
    u1 = generate_pdf_utility_bill("utility_bill.pdf", "Alex Taylor", "742 Evergreen Terrace, Springfield")
    i1 = generate_id_image("id_card_mismatch.png", "Alexander M. Taylor", "1993-11-28", "ID-992014")
    t1 = generate_id_image("id_card_tampered.png", "Alex Taylor", "1990-05-14", "ID-771822", software_tag="Adobe Photoshop 2024")
    print("Sample test documents successfully generated in backend/tests/sample_docs/")
