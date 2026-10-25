import io
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from app.services.tampering_detector import tampering_detector

def test_tampering_clean_document():
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    data = buf.getvalue()

    res = tampering_detector.analyze_document(data, "image/png", "test-doc-1")
    assert res["is_flagged"] is False
    assert res["risk_level"] == "LOW"

def test_tampering_metadata_flag():
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    # Save with Photoshop software signature via PngInfo
    info = PngInfo()
    info.add_text("Software", "Adobe Photoshop 2024")
    img.save(buf, "PNG", pnginfo=info)
    data = buf.getvalue()

    res = tampering_detector.analyze_document(data, "image/png", "test-doc-2")
    assert res["is_flagged"] is True
    assert res["software_detected"] is not None
    assert "Photoshop" in res["software_detected"]
