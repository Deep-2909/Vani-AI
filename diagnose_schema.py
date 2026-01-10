#!/usr/bin/env python3
"""
Database Schema Diagnostic Script
This will show you exactly what columns exist in your grievances table
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def diagnose_database():
    print("=" * 70)
    print("🔍 DATABASE SCHEMA DIAGNOSTIC")
    print("=" * 70)
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        inspector = inspect(engine)
        
        # Check if grievances table exists
        tables = inspector.get_table_names()
        print(f"\n📊 Available tables: {tables}")
        
        if 'grievances' not in tables:
            print("\n❌ ERROR: 'grievances' table does not exist!")
            print("\n💡 SOLUTION: Run the create_table_fixed.py script")
            return
        
        # Get column information
        print("\n" + "=" * 70)
        print("📋 CURRENT SCHEMA OF 'grievances' TABLE:")
        print("=" * 70)
        
        columns = inspector.get_columns('grievances')
        
        print(f"\n{'Column Name':<20} {'Type':<20} {'Nullable':<10} {'Default':<20}")
        print("-" * 70)
        
        for col in columns:
            col_name = col['name']
            col_type = str(col['type'])
            nullable = 'YES' if col['nullable'] else 'NO'
            default = str(col.get('default', 'None'))
            print(f"{col_name:<20} {col_type:<20} {nullable:<10} {default:<20}")
        
        # Check what columns are EXPECTED by the code
        print("\n" + "=" * 70)
        print("✅ EXPECTED COLUMNS (from your code):")
        print("=" * 70)
        expected_columns = [
            ('ticket_id', 'VARCHAR(50)', 'NO', 'UNIQUE'),
            ('citizen_name', 'VARCHAR(255)', 'YES', '-'),
            ('description', 'TEXT', 'NO', '-'),
            ('department', 'VARCHAR(100)', 'YES', '⚠️  MISSING IN YOUR DB'),
            ('status', 'VARCHAR(50)', 'YES', 'DEFAULT: OPEN'),
            ('call_id', 'VARCHAR(100)', 'YES', '-'),
            ('created_at', 'TIMESTAMP', 'YES', 'DEFAULT: NOW()')
        ]
        
        print(f"\n{'Column':<20} {'Type':<20} {'Nullable':<10} {'Notes':<20}")
        print("-" * 70)
        for col in expected_columns:
            print(f"{col[0]:<20} {col[1]:<20} {col[2]:<10} {col[3]:<20}")
        
        # Compare
        print("\n" + "=" * 70)
        print("🔍 COMPARISON:")
        print("=" * 70)
        
        current_col_names = {col['name'] for col in columns}
        expected_col_names = {col[0] for col in expected_columns}
        
        missing = expected_col_names - current_col_names
        extra = current_col_names - expected_col_names
        
        if missing:
            print(f"\n❌ MISSING COLUMNS: {missing}")
            print("   These columns are required by your code but don't exist in DB")
        
        if extra:
            print(f"\n⚠️  EXTRA COLUMNS: {extra}")
            print("   These exist in DB but aren't used by your code")
        
        if not missing and not extra:
            print("\n✅ Schema matches perfectly!")
        
        # Show sample data
        print("\n" + "=" * 70)
        print("📊 SAMPLE DATA (last 3 records):")
        print("=" * 70)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM grievances ORDER BY created_at DESC LIMIT 3"))
            rows = result.fetchall()
            
            if rows:
                # Get column names
                col_names = result.keys()
                print(f"\nColumns: {', '.join(col_names)}\n")
                
                for i, row in enumerate(rows, 1):
                    print(f"Record {i}:")
                    for col_name, value in zip(col_names, row):
                        print(f"  {col_name}: {value}")
                    print()
            else:
                print("\n(No records found)")
        
        # Provide fix
        print("=" * 70)
        print("🔧 HOW TO FIX:")
        print("=" * 70)
        
        if 'department' in missing:
            print("\n⚠️  The 'department' column is missing!")
            print("\n✅ OPTION 1: Add the missing column (RECOMMENDED)")
            print("   Run this SQL command:")
            print("\n   ALTER TABLE grievances ADD COLUMN department VARCHAR(100);")
            print("\n✅ OPTION 2: Recreate the table with correct schema")
            print("   Run: python create_table_fixed.py")
            print("\n✅ OPTION 3: Use the migration script")
            print("   Run: python migrate_database.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_database()
