import os
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/grievances.db")
engine = create_engine(DATABASE_URL)

def migrate_ticket_ids():
    print("🚀 Starting Ticket ID Migration...")
    
    with engine.connect() as conn:
        # Fetch all grievances ordered by creation time
        query = text("SELECT id, created_at, ticket_id FROM grievances ORDER BY created_at")
        grievances = conn.execute(query).fetchall()
        
        print(f"📋 Found {len(grievances)} tickets to process")
        
        # Track counts per day to generate sequential IDs
        # Format: "YYYYMMDD": count
        daily_counts = {}
        
        updated_count = 0
        
        for g in grievances:
            g_id = g[0]
            created_at = g[1]
            old_ticket_id = g[2]
            
            # Handle string dates if not datetime object
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    created_at = datetime.now()
            elif created_at is None:
                created_at = datetime.now()
                
            date_str = created_at.strftime("%Y%m%d")
            
            # Increment count for this day
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
            sequence = daily_counts[date_str]
            
            # Generate new ID
            new_ticket_id = f"DEL-{date_str}-{sequence:04d}"
            
            if old_ticket_id != new_ticket_id:
                print(f"   🔄 Updating {old_ticket_id} -> {new_ticket_id}")
                
                update_query = text("UPDATE grievances SET ticket_id = :new_id WHERE id = :id")
                conn.execute(update_query, {"new_id": new_ticket_id, "id": g_id})
                updated_count += 1
        
        conn.commit()
        print(f"✅ Migration completed. Updated {updated_count} tickets.")

if __name__ == "__main__":
    migrate_ticket_ids()
