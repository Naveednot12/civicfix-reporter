import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# --- 1. Database Setup (No Changes) ---
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite:///./civicfix.db"
)

engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)

# This small change is needed because we are no longer always using SQLite.
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = sqlalchemy.create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- 2. Defining the Table "Blueprint" (No Changes) ---
class RoutingRule(Base):
    __tablename__ = "routing_rules"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    city = sqlalchemy.Column(sqlalchemy.String)
    district = sqlalchemy.Column(sqlalchemy.String)
    issue_type = sqlalchemy.Column(sqlalchemy.String)
    contact_email = sqlalchemy.Column(sqlalchemy.String)


# --- 3. A Function to Create the Database (No Changes) ---
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


# --- 4. NEW: A Function to Add Sample Data ---
def add_sample_data():
    # Start a new conversation (session) with the database.
    db = SessionLocal()
    try:
        # Check if there is already data in the table.
        # If the first row exists, we assume data is already there and we do nothing.
        if db.query(RoutingRule).first():
            print("Database already contains data. Skipping sample data insertion.")
            return

        print("Inserting sample routing rules...")
        # Create a list of sample rules using our RoutingRule blueprint.
        # NOTE: These are fake email addresses for testing.
        sample_rules = [
            RoutingRule(city="Parangipettai", district="Bhuvanagiri", issue_type="Pothole", contact_email="naveed12092004@gmail.com"),
            RoutingRule(city="Parangipettai", district="Bhuvanagiri", issue_type="Streetlight", contact_email="naveed12092004@gmail.com"),
            RoutingRule(city="Parangipettai", district="Bhuvanagiri", issue_type="Garbage", contact_email="naveed12092004@gmail.com"),
            RoutingRule(city="Cuddalore", district="Cuddalore", issue_type="Pothole", contact_email="naveed12092004@gmail.com"),
        ]
        
        # Add all the sample rules to the session.
        db.add_all(sample_rules)
        # Commit (save) the changes to the database file.
        db.commit()
        print("Sample data inserted successfully.")

    finally:
        # Always close the conversation with the database.
        db.close()


# --- 5. Main Execution Block (Updated) ---
if __name__ == "__main__":
    print("1. Creating database and tables...")
    create_db_and_tables()
    print("   Done.")
    
    print("\n2. Adding sample data...")
    add_sample_data()
    print("   Done.")