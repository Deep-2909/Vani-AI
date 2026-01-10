#!/usr/bin/env python3
"""
Quick Fix: Add Missing 'department' Column
This script safely adds the department column to your existing table
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def add_department_column():
    print("=" * 70)
    print("🔧 ADDING MISSING 'department' COLUMN")
    print("=" * 70)
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        
        print("\n1️⃣  Checking if column already exists...")
        
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'grievances' AND column_name = 'department'
            """))
            
            exists = result.fetchone() is not None
            
            if exists:
                print("✅ Column 'department' already exists!")
                return
        
        print("❌ Column 'department' does not exist")
        print("\n2️⃣  Adding 'department' column...")
        
        with engine.begin() as conn:
            # Add the column
            conn.execute(text("""
                ALTER TABLE grievances 
                ADD COLUMN department VARCHAR(100)
            """))
            
            print("✅ Column added successfully!")
        
        print("\n3️⃣  Verifying the change...")
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'grievances' AND column_name = 'department'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Verified: {row[0]} ({row[1]}({row[2]}))")
            else:
                print("⚠️  Could not verify column")
        
        print("\n4️⃣  Updating existing records with default department...")
        
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE grievances 
                SET department = 'General/PGC'
                WHERE department IS NULL
            """))
            
            print(f"✅ Updated {result.rowcount} records")
        
        print("\n" + "=" * 70)
        print("✅ FIX COMPLETE!")
        print("=" * 70)
        print("\nYou can now restart your application and try again.")
        print("The complaint registration should work properly now.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 70)
        print("💡 ALTERNATIVE FIX:")
        print("=" * 70)
        print("\nIf the script failed, you can add the column manually:")
        print("\n1. Connect to your database:")
        print(f"   psql -U grievance_user -d grievance_ai")
        print("\n2. Run this command:")
        print("   ALTER TABLE grievances ADD COLUMN department VARCHAR(100);")
        print("\n3. Exit psql:")
        print("   \\q")

if __name__ == "__main__":
    add_department_column()
