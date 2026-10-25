import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.application import ApplicationProfile, UserApplication
from app.utils.security import get_password_hash
from app.routers.applications import seed_profiles_if_empty

def create_demo_accounts():
    print("==================================================")
    print("      Creating DocVerify AI Demo Accounts        ")
    print("==================================================")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed application profiles if needed
        seed_profiles_if_empty(db)

        # 1. Demo Applicant Account
        user_email = "demo@docverify.ai"
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = User(
                email=user_email,
                full_name="Demo Applicant",
                hashed_password=get_password_hash("Password123!"),
                role="USER",
                is_active=True
            )
            db.add(user)
            print(f"[OK] Created Applicant Account: {user_email}")
        else:
            user.hashed_password = get_password_hash("Password123!")
            user.is_active = True
            print(f"[OK] Updated Applicant Account: {user_email}")

        # 2. Demo Administrator Account
        admin_email = "admin@docverify.ai"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                full_name="Demo Administrator",
                hashed_password=get_password_hash("AdminPassword123!"),
                role="ADMIN",
                is_active=True
            )
            db.add(admin)
            print(f"[OK] Created Administrator Account: {admin_email}")
        else:
            admin.hashed_password = get_password_hash("AdminPassword123!")
            admin.is_active = True
            print(f"[OK] Updated Administrator Account: {admin_email}")

        db.commit()
        print("\n==================================================")
        print("Demo accounts ready for instant login!")
        print("--------------------------------------------------")
        print("1. USER / APPLICANT ACCOUNT:")
        print("   Email:    demo@docverify.ai")
        print("   Password: Password123!")
        print("   Role:     USER")
        print("--------------------------------------------------")
        print("2. ADMINISTRATOR ACCOUNT:")
        print("   Email:    admin@docverify.ai")
        print("   Password: AdminPassword123!")
        print("   Role:     ADMIN")
        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    create_demo_accounts()
