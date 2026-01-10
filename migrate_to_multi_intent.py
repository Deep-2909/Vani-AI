#!/usr/bin/env python3
"""
Database Migration Script for Multi-Intent System
Adds new columns and tables for enhanced functionality
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def migrate_to_multi_intent():
    print("=" * 70)
    print("🔄 MIGRATING TO MULTI-INTENT SYSTEM")
    print("=" * 70)
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        
        print("\n📋 Step 1: Adding new columns to 'grievances' table...")
        
        with engine.begin() as conn:
            # Add new columns if they don't exist
            columns_to_add = [
                ("contact", "VARCHAR(15)"),
                ("location", "VARCHAR(500)"),
                ("category", "VARCHAR(100)"),
                ("priority", "VARCHAR(20)"),
                ("escalated", "INTEGER DEFAULT 0"),
                ("escalation_reason", "TEXT"),
                ("updated_at", "TIMESTAMP WITH TIME ZONE"),
                ("resolved_at", "TIMESTAMP WITH TIME ZONE"),
                ("assigned_to", "VARCHAR(255)"),
                ("remarks", "TEXT")
            ]
            
            inspector = inspect(engine)
            existing_columns = {col['name'] for col in inspector.get_columns('grievances')}
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    print(f"   Adding column: {col_name}")
                    conn.execute(text(f"ALTER TABLE grievances ADD COLUMN {col_name} {col_type}"))
                else:
                    print(f"   ✓ Column exists: {col_name}")
        
        print("\n✅ Grievances table updated")
        
        # ===================================================================
        # Create new tables
        # ===================================================================
        
        print("\n📋 Step 2: Creating new tables...")
        
        with engine.begin() as conn:
            # Status Checks table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS status_checks (
                    id SERIAL PRIMARY KEY,
                    ticket_id VARCHAR(50) NOT NULL,
                    phone_number VARCHAR(15),
                    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    call_id VARCHAR(100)
                );
                CREATE INDEX IF NOT EXISTS idx_status_checks_ticket ON status_checks(ticket_id);
            """))
            print("   ✓ status_checks table created")
            
            # Escalations table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS escalations (
                    id SERIAL PRIMARY KEY,
                    ticket_id VARCHAR(50) NOT NULL,
                    reason TEXT NOT NULL,
                    escalated_by VARCHAR(15),
                    escalated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    escalated_to VARCHAR(255),
                    call_id VARCHAR(100)
                );
                CREATE INDEX IF NOT EXISTS idx_escalations_ticket ON escalations(ticket_id);
            """))
            print("   ✓ escalations table created")
            
            # Feedback table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    ticket_id VARCHAR(50),
                    rating INTEGER NOT NULL,
                    feedback_text TEXT NOT NULL,
                    phone_number VARCHAR(15),
                    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    call_id VARCHAR(100)
                );
                CREATE INDEX IF NOT EXISTS idx_feedback_ticket ON feedback(ticket_id);
            """))
            print("   ✓ feedback table created")
            
            # Emergencies table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS emergencies (
                    id SERIAL PRIMARY KEY,
                    emergency_type VARCHAR(50) NOT NULL,
                    location VARCHAR(500) NOT NULL,
                    phone_number VARCHAR(15) NOT NULL,
                    description TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'PENDING',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    responded_at TIMESTAMP WITH TIME ZONE,
                    call_id VARCHAR(100)
                );
                CREATE INDEX IF NOT EXISTS idx_emergencies_type ON emergencies(emergency_type);
                CREATE INDEX IF NOT EXISTS idx_emergencies_status ON emergencies(status);
            """))
            print("   ✓ emergencies table created")
        
        print("\n✅ All new tables created")
        
        # ===================================================================
        # Update existing data with defaults
        # ===================================================================
        
        print("\n📋 Step 3: Updating existing records with default values...")
        
        with engine.begin() as conn:
            # Set default priority for existing complaints
            result = conn.execute(text("""
                UPDATE grievances 
                SET priority = 'Medium'
                WHERE priority IS NULL
            """))
            print(f"   ✓ Updated {result.rowcount} records with default priority")
            
            # Set default category
            result = conn.execute(text("""
                UPDATE grievances 
                SET category = 'Other'
                WHERE category IS NULL
            """))
            print(f"   ✓ Updated {result.rowcount} records with default category")
        
        # ===================================================================
        # Verify schema
        # ===================================================================
        
        print("\n📋 Step 4: Verifying final schema...")
        
        inspector = inspect(engine)
        
        tables = inspector.get_table_names()
        expected_tables = ['grievances', 'status_checks', 'escalations', 'feedback', 'emergencies']
        
        print("\n   Tables:")
        for table in expected_tables:
            status = "✓" if table in tables else "✗"
            print(f"   {status} {table}")
        
        # Check grievances columns
        grievances_cols = {col['name'] for col in inspector.get_columns('grievances')}
        required_cols = ['ticket_id', 'citizen_name', 'contact', 'description', 'location',
                        'department', 'category', 'priority', 'status', 'call_id']
        
        print("\n   Grievances columns:")
        for col in required_cols:
            status = "✓" if col in grievances_cols else "✗"
            print(f"   {status} {col}")
        
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 70)
        print("\n📊 Your database now supports:")
        print("   ✓ Complaint registration with category & priority")
        print("   ✓ Status checking")
        print("   ✓ Escalations")
        print("   ✓ Feedback collection")
        print("   ✓ Emergency alerts")
        print("\n💡 Next steps:")
        print("   1. Replace app/services/llm.py with llm_multi_intent.py")
        print("   2. Replace app/api/retell_ws.py with retell_ws_multi_intent.py")
        print("   3. Update app/models/grievance.py with models_enhanced.py")
        print("   4. Restart your application")
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️  This will add new columns and tables to your database")
    print("Existing data will be preserved")
    
    response = input("\nContinue with migration? (yes/no): ").strip().lower()
    
    if response == 'yes':
        migrate_to_multi_intent()
    else:
        print("\nMigration cancelled")
