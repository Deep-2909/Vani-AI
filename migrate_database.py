#!/usr/bin/env python3
"""
Complete Database Migration Script
This ensures your database schema matches what the code expects
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def migrate_database():
    print("=" * 70)
    print("🔄 DATABASE MIGRATION SCRIPT")
    print("=" * 70)
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        inspector = inspect(engine)
        
        # Step 1: Check if table exists
        print("\n1️⃣  Checking if 'grievances' table exists...")
        tables = inspector.get_table_names()
        
        if 'grievances' not in tables:
            print("❌ Table does not exist")
            print("\n2️⃣  Creating table...")
            create_table(engine)
        else:
            print("✅ Table exists")
            print("\n2️⃣  Checking schema...")
            migrate_schema(engine, inspector)
        
        # Step 3: Verify final schema
        print("\n3️⃣  Verifying final schema...")
        verify_schema(engine)
        
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 70)
        print("\nYour database is now ready. Restart your application.")
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()

def create_table(engine):
    """Create the grievances table from scratch"""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE grievances (
                id SERIAL PRIMARY KEY,
                ticket_id VARCHAR(50) UNIQUE NOT NULL,
                citizen_name VARCHAR(255),
                description TEXT NOT NULL,
                department VARCHAR(100),
                status VARCHAR(50) DEFAULT 'OPEN',
                call_id VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create indexes
        conn.execute(text("CREATE INDEX idx_ticket_id ON grievances(ticket_id)"))
        conn.execute(text("CREATE INDEX idx_status ON grievances(status)"))
        conn.execute(text("CREATE INDEX idx_call_id ON grievances(call_id)"))
        
    print("✅ Table created successfully")

def migrate_schema(engine, inspector):
    """Update existing table schema"""
    columns = {col['name']: col for col in inspector.get_columns('grievances')}
    
    required_columns = {
        'id': 'SERIAL PRIMARY KEY',
        'ticket_id': 'VARCHAR(50) UNIQUE NOT NULL',
        'citizen_name': 'VARCHAR(255)',
        'description': 'TEXT NOT NULL',
        'department': 'VARCHAR(100)',
        'status': 'VARCHAR(50) DEFAULT \'OPEN\'',
        'call_id': 'VARCHAR(100)',
        'created_at': 'TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP'
    }
    
    migrations = []
    
    for col_name, col_def in required_columns.items():
        if col_name not in columns:
            migrations.append((col_name, col_def))
            print(f"   ❌ Missing column: {col_name}")
    
    if not migrations:
        print("✅ Schema is up to date")
        return
    
    print(f"\n   Found {len(migrations)} columns to add")
    
    with engine.begin() as conn:
        for col_name, col_def in migrations:
            print(f"   Adding: {col_name}...")
            
            # Simplified ADD COLUMN (without defaults in ALTER)
            if 'DEFAULT' in col_def:
                # Extract the default value
                if 'CURRENT_TIMESTAMP' in col_def:
                    conn.execute(text(f"""
                        ALTER TABLE grievances 
                        ADD COLUMN {col_name} TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    """))
                elif "'OPEN'" in col_def:
                    conn.execute(text(f"""
                        ALTER TABLE grievances 
                        ADD COLUMN {col_name} VARCHAR(50) DEFAULT 'OPEN'
                    """))
                else:
                    # Generic case
                    base_type = col_def.split('DEFAULT')[0].strip()
                    conn.execute(text(f"""
                        ALTER TABLE grievances 
                        ADD COLUMN {col_name} {base_type}
                    """))
            else:
                # No default
                conn.execute(text(f"""
                    ALTER TABLE grievances 
                    ADD COLUMN {col_name} {col_def.replace('NOT NULL', '')}
                """))
            
            print(f"   ✅ Added: {col_name}")
        
        # Add indexes if missing
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ticket_id ON grievances(ticket_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_status ON grievances(status)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_call_id ON grievances(call_id)"))
            print("   ✅ Indexes updated")
        except:
            pass  # Indexes might already exist

def verify_schema(engine):
    """Verify the final schema"""
    inspector = inspect(engine)
    columns = inspector.get_columns('grievances')
    
    expected = {'id', 'ticket_id', 'citizen_name', 'description', 'department', 
                'status', 'call_id', 'created_at'}
    actual = {col['name'] for col in columns}
    
    missing = expected - actual
    
    if missing:
        print(f"   ⚠️  Still missing: {missing}")
        raise Exception(f"Schema verification failed. Missing columns: {missing}")
    
    print("   ✅ All required columns present")
    
    # Show final schema
    print("\n   Final schema:")
    for col in columns:
        print(f"   - {col['name']}: {col['type']}")

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will modify your database schema")
    print("Make sure you have a backup if you have important data")
    
    response = input("\nContinue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        migrate_database()
    else:
        print("\nMigration cancelled")
