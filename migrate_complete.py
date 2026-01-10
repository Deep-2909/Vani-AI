#!/usr/bin/env python3
"""
Complete Database Migration for Advanced Features
Adds:
1. Multilingual support
2. Area hotspot tracking
3. Outbound calls
4. Resolved complaints archive
5. Government schemes
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def migrate_complete_system():
    print("=" * 80)
    print("🚀 COMPLETE SYSTEM MIGRATION")
    print("=" * 80)
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        
        # ===================================================================
        # Step 1: Update grievances table
        # ===================================================================
        print("\n📋 Step 1: Updating grievances table...")
        
        with engine.begin() as conn:
            inspector = inspect(engine)
            existing_columns = {col['name'] for col in inspector.get_columns('grievances')}
            
            new_columns = [
                ("contact", "VARCHAR(15)"),
                ("location", "VARCHAR(500)"),
                ("area", "VARCHAR(200)"),
                ("category", "VARCHAR(100)"),
                ("priority", "VARCHAR(20)"),
                ("escalated", "INTEGER DEFAULT 0"),
                ("escalation_reason", "TEXT"),
                ("updated_at", "TIMESTAMP WITH TIME ZONE"),
                ("resolved_at", "TIMESTAMP WITH TIME ZONE"),
                ("assigned_to", "VARCHAR(255)"),
                ("remarks", "TEXT"),
                ("language", "VARCHAR(20) DEFAULT 'english'")
            ]
            
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    print(f"   Adding column: {col_name}")
                    conn.execute(text(f"ALTER TABLE grievances ADD COLUMN {col_name} {col_type}"))
                else:
                    print(f"   ✓ Column exists: {col_name}")
            
            # Add indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_grievances_area ON grievances(area)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_grievances_created ON grievances(created_at)"))
        
        print("✅ Grievances table updated")
        
        # ===================================================================
        # Step 2: Create complaints_resolved table
        # ===================================================================
        print("\n📋 Step 2: Creating complaints_resolved table...")
        
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS complaints_resolved (
                    id SERIAL PRIMARY KEY,
                    ticket_id VARCHAR(50) UNIQUE NOT NULL,
                    citizen_name VARCHAR(255),
                    contact VARCHAR(15),
                    description TEXT,
                    location VARCHAR(500),
                    area VARCHAR(200),
                    department VARCHAR(100),
                    category VARCHAR(100),
                    priority VARCHAR(20),
                    call_id VARCHAR(100),
                    resolved_by VARCHAR(255) NOT NULL,
                    resolution_notes TEXT,
                    resolution_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    complaint_created_at TIMESTAMP WITH TIME ZONE,
                    complaint_resolved_at TIMESTAMP WITH TIME ZONE,
                    resolution_time_hours FLOAT,
                    citizen_rating INTEGER,
                    citizen_feedback TEXT,
                    transferred_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    transferred_by VARCHAR(255)
                );
                
                CREATE INDEX IF NOT EXISTS idx_resolved_ticket ON complaints_resolved(ticket_id);
                CREATE INDEX IF NOT EXISTS idx_resolved_area ON complaints_resolved(area);
                CREATE INDEX IF NOT EXISTS idx_resolved_dept ON complaints_resolved(department);
                CREATE INDEX IF NOT EXISTS idx_resolved_date ON complaints_resolved(resolution_date);
            """))
        
        print("✅ complaints_resolved table created")
        
        # ===================================================================
        # Step 3: Create area_hotspots table
        # ===================================================================
        print("\n📋 Step 3: Creating area_hotspots table...")
        
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS area_hotspots (
                    id SERIAL PRIMARY KEY,
                    area_name VARCHAR(200) UNIQUE NOT NULL,
                    normalized_name VARCHAR(200) UNIQUE NOT NULL,
                    total_complaints INTEGER DEFAULT 0,
                    open_complaints INTEGER DEFAULT 0,
                    resolved_complaints INTEGER DEFAULT 0,
                    water_complaints INTEGER DEFAULT 0,
                    road_complaints INTEGER DEFAULT 0,
                    electricity_complaints INTEGER DEFAULT 0,
                    pollution_complaints INTEGER DEFAULT 0,
                    other_complaints INTEGER DEFAULT 0,
                    critical_complaints INTEGER DEFAULT 0,
                    high_complaints INTEGER DEFAULT 0,
                    medium_complaints INTEGER DEFAULT 0,
                    low_complaints INTEGER DEFAULT 0,
                    is_hotspot BOOLEAN DEFAULT FALSE,
                    hotspot_level VARCHAR(20),
                    flagged_at TIMESTAMP WITH TIME ZONE,
                    warning_threshold INTEGER DEFAULT 10,
                    critical_threshold INTEGER DEFAULT 25,
                    severe_threshold INTEGER DEFAULT 50,
                    first_complaint_at TIMESTAMP WITH TIME ZONE,
                    last_complaint_at TIMESTAMP WITH TIME ZONE,
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    alert_sent BOOLEAN DEFAULT FALSE,
                    alert_sent_at TIMESTAMP WITH TIME ZONE
                );
                
                CREATE INDEX IF NOT EXISTS idx_hotspots_area ON area_hotspots(normalized_name);
                CREATE INDEX IF NOT EXISTS idx_hotspots_flag ON area_hotspots(is_hotspot);
            """))
        
        print("✅ area_hotspots table created")
        
        # ===================================================================
        # Step 4: Create outbound_calls table
        # ===================================================================
        print("\n📋 Step 4: Creating outbound_calls table...")
        
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS outbound_calls (
                    id SERIAL PRIMARY KEY,
                    call_id VARCHAR(100) UNIQUE,
                    phone_number VARCHAR(15) NOT NULL,
                    call_type VARCHAR(50) NOT NULL,
                    message_template VARCHAR(100),
                    message_content TEXT,
                    related_ticket_id VARCHAR(50),
                    scheme_name VARCHAR(255),
                    alert_type VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'PENDING',
                    scheduled_at TIMESTAMP WITH TIME ZONE,
                    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP WITH TIME ZONE,
                    duration_seconds INTEGER,
                    answered BOOLEAN DEFAULT FALSE,
                    user_response TEXT,
                    action_taken VARCHAR(100),
                    initiated_by VARCHAR(255),
                    language VARCHAR(20) DEFAULT 'hindi'
                );
                
                CREATE INDEX IF NOT EXISTS idx_outbound_call_id ON outbound_calls(call_id);
                CREATE INDEX IF NOT EXISTS idx_outbound_phone ON outbound_calls(phone_number);
                CREATE INDEX IF NOT EXISTS idx_outbound_type ON outbound_calls(call_type);
                CREATE INDEX IF NOT EXISTS idx_outbound_status ON outbound_calls(status);
            """))
        
        print("✅ outbound_calls table created")
        
        # ===================================================================
        # Step 5: Create government_schemes table
        # ===================================================================
        print("\n📋 Step 5: Creating government_schemes table...")
        
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS government_schemes (
                    id SERIAL PRIMARY KEY,
                    scheme_code VARCHAR(50) UNIQUE NOT NULL,
                    scheme_name VARCHAR(255) NOT NULL,
                    department VARCHAR(100),
                    short_description TEXT,
                    full_description TEXT,
                    eligibility_criteria TEXT,
                    target_areas TEXT,
                    target_categories TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    start_date TIMESTAMP WITH TIME ZONE,
                    end_date TIMESTAMP WITH TIME ZONE,
                    send_notifications BOOLEAN DEFAULT FALSE,
                    notification_message TEXT,
                    application_url VARCHAR(500),
                    helpline_number VARCHAR(15),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                );
                
                CREATE INDEX IF NOT EXISTS idx_schemes_code ON government_schemes(scheme_code);
                CREATE INDEX IF NOT EXISTS idx_schemes_active ON government_schemes(is_active);
            """))
        
        print("✅ government_schemes table created")
        
        # ===================================================================
        # Step 6: Populate initial data
        # ===================================================================
        print("\n📋 Step 6: Populating initial data...")
        
        with engine.begin() as conn:
            # Update existing records with default values
            conn.execute(text("""
                UPDATE grievances 
                SET priority = 'Medium', 
                    category = 'Other',
                    language = 'english'
                WHERE priority IS NULL OR category IS NULL OR language IS NULL
            """))
            
            # Insert sample government scheme
            conn.execute(text("""
                INSERT INTO government_schemes 
                (scheme_code, scheme_name, department, short_description, 
                 notification_message, is_active)
                VALUES 
                ('SAMPLE001', 'Sample Government Scheme', 'General/PGC',
                 'This is a sample scheme for testing',
                 'Namaste, aapke liye ek naya sarkari yojana hai.',
                 FALSE)
                ON CONFLICT (scheme_code) DO NOTHING
            """))
        
        print("✅ Initial data populated")
        
        # ===================================================================
        # Verification
        # ===================================================================
        print("\n📋 Step 7: Verifying migration...")
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'grievances',
            'complaints_resolved',
            'area_hotspots',
            'outbound_calls',
            'government_schemes',
            'status_checks',
            'escalations',
            'feedback',
            'emergencies'
        ]
        
        print("\n   Tables:")
        all_present = True
        for table in expected_tables:
            status = "✓" if table in tables else "✗"
            print(f"   {status} {table}")
            if table not in tables:
                all_present = False
        
        if not all_present:
            print("\n⚠️  Some tables are missing!")
            return
        
        # ===================================================================
        # Success
        # ===================================================================
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 80)
        
        print("\n📊 Your system now supports:")
        print("   ✅ Multilingual voice (Hindi, Punjabi, English)")
        print("   ✅ Area hotspot tracking with auto-flagging")
        print("   ✅ Outbound calls for schemes & alerts")
        print("   ✅ Complaint resolution archive")
        print("   ✅ Government scheme management")
        
        print("\n📝 Next steps:")
        print("   1. Update your code files:")
        print("      - app/services/llm.py → llm_multilingual.py")
        print("      - app/models/grievance.py → models_complete.py")
        print("      - Add app/api/manager.py → manager_api.py")
        print("      - Add app/services/area_hotspot.py → area_hotspot_service.py")
        print("      - Add app/services/outbound.py → outbound_call_service.py")
        print("   2. Update main.py to include manager router")
        print("   3. Configure environment variables:")
        print("      - RETELL_API_KEY")
        print("      - RETELL_FROM_NUMBER")
        print("      - RETELL_AGENT_ID")
        print("      - MANAGER_PHONE_NUMBERS")
        print("   4. Restart your application")
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n⚠️  This migration will add new tables and columns")
    print("Existing data will be preserved")
    
    response = input("\nContinue with migration? (yes/no): ").strip().lower()
    
    if response == 'yes':
        migrate_complete_system()
    else:
        print("\nMigration cancelled")
