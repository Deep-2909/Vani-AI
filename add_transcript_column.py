#!/usr/bin/env python3
"""
Add transcript column to grievances table
This allows storing call transcripts fetched from Retell API
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def add_transcript_column():
    print("=" * 80)
    print("🚀 ADDING TRANSCRIPT COLUMN TO GRIEVANCES TABLE")
    print("=" * 80)

    try:
        engine = create_engine(DATABASE_URL, echo=False)

        with engine.begin() as conn:
            # Check if column already exists
            inspector = inspect(engine)
            existing_columns = {col['name'] for col in inspector.get_columns('grievances')}

            if 'transcript' in existing_columns:
                print("✅ Column 'transcript' already exists")
            else:
                print("📋 Adding 'transcript' column...")
                conn.execute(text("ALTER TABLE grievances ADD COLUMN transcript TEXT"))
                print("✅ Added 'transcript' column")

            if 'retell_call_id' in existing_columns:
                print("✅ Column 'retell_call_id' already exists")
            else:
                print("📋 Adding 'retell_call_id' column...")
                conn.execute(text("ALTER TABLE grievances ADD COLUMN retell_call_id VARCHAR(100)"))
                print("✅ Added 'retell_call_id' column")

                # Add index for faster lookups
                print("📋 Adding index on retell_call_id...")
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_grievances_retell_call ON grievances(retell_call_id)"))
                print("✅ Added index")

        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    add_transcript_column()
