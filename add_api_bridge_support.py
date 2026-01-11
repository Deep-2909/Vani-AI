#!/usr/bin/env python3
"""
Database Migration to Support API Bridge Features
Run this ONLY if you get column errors when using the API bridge

Usage: python add_api_bridge_support.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def check_column_exists(conn, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_database():
    print("=" * 70)
    print("🔧 API BRIDGE DATABASE MIGRATION")
    print("=" * 70)
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        
        print("\n📋 Checking database structure...")
        
        with engine.begin() as conn:
            # Check if tables exist
            inspector = inspect(conn)
            tables = inspector.get_table_names()
            
            if 'grievances' not in tables:
                print("❌ Error: 'grievances' table does not exist!")
                print("💡 Please run your main migration first")
                return
            
            print("✅ Grievances table exists")
            
            # ============================================================
            # Add missing columns to grievances table if needed
            # ============================================================
            
            columns_to_add = [
                ('contact', 'VARCHAR(15)'),
                ('location', 'VARCHAR(500)'),
                ('area', 'VARCHAR(200)'),
                ('category', 'VARCHAR(100)'),
                ('priority', 'VARCHAR(20)'),
                ('escalated', 'INTEGER DEFAULT 0'),
                ('escalation_reason', 'TEXT'),
                ('updated_at', 'TIMESTAMP WITH TIME ZONE'),
                ('resolved_at', 'TIMESTAMP WITH TIME ZONE'),
                ('assigned_to', 'VARCHAR(255)'),
                ('remarks', 'TEXT'),
                ('language', 'VARCHAR(20) DEFAULT \'english\'')
            ]
            
            added_count = 0
            for col_name, col_type in columns_to_add:
                if not check_column_exists(conn, 'grievances', col_name):
                    print(f"   Adding column: {col_name}")
                    conn.execute(text(f"""
                        ALTER TABLE grievances 
                        ADD COLUMN {col_name} {col_type}
                    """))
                    added_count += 1
                else:
                    print(f"   ✓ Column exists: {col_name}")
            
            if added_count > 0:
                print(f"\n✅ Added {added_count} new columns to grievances table")
            else:
                print("\n✅ All required columns already exist in grievances table")
            
            # ============================================================
            # Check outbound_calls table
            # ============================================================
            
            if 'outbound_calls' in tables:
                print("\n📋 Checking outbound_calls table...")
                
                outbound_columns = [
                    ('scheduled_at', 'TIMESTAMP WITH TIME ZONE'),
                    ('message_content', 'TEXT')
                ]
                
                for col_name, col_type in outbound_columns:
                    if not check_column_exists(conn, 'outbound_calls', col_name):
                        print(f"   Adding column: {col_name}")
                        conn.execute(text(f"""
                            ALTER TABLE outbound_calls 
                            ADD COLUMN {col_name} {col_type}
                        """))
                    else:
                        print(f"   ✓ Column exists: {col_name}")
                
                print("✅ Outbound_calls table is ready")
            else:
                print("\n⚠️  Warning: outbound_calls table does not exist")
                print("   This is OK if you haven't run migrate_complete.py yet")
            
            # ============================================================
            # Add indexes for better performance
            # ============================================================
            
            print("\n📋 Adding performance indexes...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_grievances_contact ON grievances(contact)",
                "CREATE INDEX IF NOT EXISTS idx_grievances_area ON grievances(area)",
                "CREATE INDEX IF NOT EXISTS idx_grievances_category ON grievances(category)",
                "CREATE INDEX IF NOT EXISTS idx_grievances_priority ON grievances(priority)",
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    # Index might already exist, that's fine
                    pass
            
            print("✅ Indexes created")
            
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 70)
        
        print("\n📊 Summary:")
        print("   ✓ All required columns are present")
        print("   ✓ Indexes created for performance")
        print("   ✓ Database is ready for API bridge")
        
        print("\n🚀 Next steps:")
        print("   1. Add api_bridge.py to app/api/ folder")
        print("   2. Update main.py to include bridge router")
        print("   3. Restart your backend server")
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Troubleshooting:")
        print("   1. Check if DATABASE_URL in .env is correct")
        print("   2. Verify database connection")
        print("   3. Check if you have ALTER TABLE permissions")


if __name__ == "__main__":
    print("\n⚠️  This script will modify your database structure")
    print("It's safe to run - existing data will NOT be lost")
    
    response = input("\nContinue with migration? (yes/no): ").strip().lower()
    
    if response == 'yes':
        migrate_database()
    else:
        print("\nMigration cancelled")
