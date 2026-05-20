"""Create an admin user. Usage: uv run python scripts/create_admin.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from auth.security import hash_password
from database import SessionLocal, init_db
from models.user import User


def main() -> None:
    init_db()
    name = input("Name: ").strip()
    phone = input("Phone: ").strip()
    password = input("Password: ").strip()

    if not name or not phone or not password:
        print("All fields are required")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.phone == phone).first()
        if existing:
            existing.is_admin = True
            existing.password_hash = hash_password(password)
            existing.name = name
            db.commit()
            print(f"User {phone} updated to admin")
        else:
            user = User(
                name=name,
                phone=phone,
                password_hash=hash_password(password),
                is_admin=True,
            )
            db.add(user)
            db.commit()
            print(f"Admin user {phone} created")
    finally:
        db.close()


if __name__ == "__main__":
    main()
