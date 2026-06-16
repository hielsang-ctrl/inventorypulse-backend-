"""Run this once after migrations to seed an admin user and sample data."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.supplier import Supplier
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

# Admin user
if not db.query(User).filter(User.email == "admin@inventorypulse.com").first():
    db.add(User(
        name="Admin",
        email="admin@inventorypulse.com",
        hashed_password=pwd_context.hash("Admin@1234"),
        role=UserRole.admin,
    ))
    print("Created admin user: admin@inventorypulse.com / Admin@1234")

# Categories
for name in ["Electronics", "Office Supplies", "Raw Materials", "Finished Goods"]:
    if not db.query(Category).filter(Category.name == name).first():
        db.add(Category(name=name))

# Suppliers
for s in [
    {"name": "Acme Corp", "contact_name": "Jane Doe", "phone": "+254700000001", "email": "jane@acme.com"},
    {"name": "Global Parts Ltd", "contact_name": "John Smith", "phone": "+254700000002", "email": "john@globalparts.com"},
]:
    if not db.query(Supplier).filter(Supplier.name == s["name"]).first():
        db.add(Supplier(**s))

db.commit()
db.close()
print("Seed complete.")
