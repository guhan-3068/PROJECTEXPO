import pytest
from app.services.guidance_service import guidance_service, OFFICIAL_GOVERNMENT_SERVICES, CORRECTION_GUIDES
from app.database import SessionLocal
from app.models.user import User
from app.services.demo_service import demo_service
from app.routers.verification import run_verification

def test_official_services_catalog():
    services = guidance_service.get_all_official_services()
    assert len(services) >= 10
    
    # Check essential portals are present
    domains = [s["official_url"] for s in services]
    assert any("uidai.gov.in" in d for d in domains)
    assert any("incometax.gov.in" in d for d in domains)
    assert any("parivahan.gov.in" in d for d in domains)
    assert any("tnesevai.tn.gov.in" in d for d in domains)
    assert any("digilocker.gov.in" in d for d in domains)

def test_correction_guides_have_9_points_and_tamil():
    guides = guidance_service.get_all_correction_guides()
    assert len(guides) >= 6
    
    name_guide = guidance_service.get_correction_guide("name_mismatch")
    assert name_guide is not None
    assert "title_ta" in name_guide
    sec = name_guide["sections"]
    assert "what_is_issue" in sec
    assert "why_it_causes_problem" in sec
    assert "which_doc_needs_attention" in sec
    assert "who_is_authorized" in sec
    assert "official_correction_process" in sec
    assert "supporting_docs_needed" in sec
    assert "official_service_portal" in sec
    assert "after_correction" in sec
    assert "what_to_recheck" in sec
    # Check Tamil explanations present
    assert "what_is_issue_ta" in sec
    assert "official_correction_process_ta" in sec

def test_demo_scenario_generates_action_plan_and_readiness():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@docverify.ai").first()
        app = demo_service.load_demo_scenario("missing_income_cert", user, db)
        assert app is not None
        assert app.verification_result is not None
        
        ver_res = app.verification_result
        checklist = ver_res.get_json_field("prioritized_checklist")
        plan = ver_res.get_json_field("action_plan")
        
        assert len(checklist) > 0
        assert len(plan) > 0
        # Missing income certificate should be marked as CRITICAL action
        assert any(p["urgency"] == "CRITICAL" for p in plan)
        assert ver_res.readiness_status in ["Action Required", "Needs Manual Review", "Ready for Next Step"]
    finally:
        db.close()
