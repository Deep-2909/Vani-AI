#!/usr/bin/env python3
"""
Add call_duration column to grievances table
This stores the actual call duration in seconds from Retell
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def add_call_duration_column():
    print("=" * 80)
    print("🚀 ADDING CALL_DURATION COLUMN TO GRIEVANCES TABLE")
    print("=" * 80)

    try:
        engine = create_engine(DATABASE_URL, echo=False)

        with engine.begin() as conn:
            # Check if column already exists
            inspector = inspect(engine)
            existing_columns = {col['name'] for col in inspector.get_columns('grievances')}

            if 'call_duration' in existing_columns:
                print("✅ Column 'call_duration' already exists")
            else:
                print("📋 Adding 'call_duration' column...")
                conn.execute(text("ALTER TABLE grievances ADD COLUMN call_duration INTEGER DEFAULT 0"))
                print("✅ Added 'call_duration' column (stores duration in seconds)")

        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    add_call_duration_column()
