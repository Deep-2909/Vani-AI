#!/usr/bin/env python3
"""
View All Database Tables
Beautiful formatted output of all tables in the grievance system
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://grievance_user:yourpassword@localhost:5432/grievance_ai"
)

def format_value(value, max_length=50):
    """Format a value for display"""
    if value is None:
        return "NULL"
    
    # Handle datetime
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
    # Convert to string and truncate if needed
    str_value = str(value)
    if len(str_value) > max_length:
        return str_value[:max_length-3] + "..."
    return str_value


def print_table(name, rows, columns):
    """Print a formatted table"""
    print(f"\n{'='*120}")
    print(f"📊 {name}")
    print(f"{'='*120}")
    
    if not rows:
        print("   ⚠️  No data in this table")
        return
    
    # Convert columns to list if needed
    columns = list(columns)
    
    # Calculate column widths
    col_widths = {}
    for col in columns:
        col_widths[col] = len(col)
    
    # Check data widths
    for row in rows:
        for i, col in enumerate(columns):
            value_len = len(format_value(row[i], max_length=50))
            col_widths[col] = max(col_widths[col], value_len)
    
    # Print header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows:
        row_str = " | ".join(
            format_value(row[i], max_length=50).ljust(col_widths[columns[i]]) 
            for i in range(len(columns))
        )
        print(row_str)
    
    print(f"\n   Total: {len(rows)} records")


def view_all_tables():
    """View all tables in the database"""
    print("\n" + "="*120)
    print("🗄️  DELHI GRIEVANCE AI SYSTEM - DATABASE VIEWER")
    print("="*120)
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        
        with engine.connect() as conn:
            
            # ===================================================================
            # TABLE 1: GRIEVANCES
            # ===================================================================
            result = conn.execute(text("""
                SELECT 
                    id,
                    ticket_id,
                    citizen_name,
                    contact,
                    LEFT(description, 40) as description,
                    location,
                    area,
                    category,
                    priority,
                    department,
                    status,
                    language,
                    created_at
                FROM grievances 
                ORDER BY created_at DESC 
                LIMIT 50
            """))
            
            rows = result.fetchall()
            columns = result.keys()
            print_table("GRIEVANCES (Recent 50)", rows, columns)
            
            # ===================================================================
            # TABLE 2: AREA HOTSPOTS
            # ===================================================================
            result = conn.execute(text("""
                SELECT 
                    id,
                    area_name,
                    normalized_name,
                    total_complaints,
                    open_complaints,
                    resolved_complaints,
                    water_complaints,
                    road_complaints,
                    electricity_complaints,
                    is_hotspot,
                    hotspot_level,
                    last_complaint_at
                FROM area_hotspots 
                ORDER BY open_complaints DESC 
                LIMIT 50
            """))
            
            rows = result.fetchall()
            columns = result.keys()
            print_table("AREA HOTSPOTS (Top 50 by Open Complaints)", rows, columns)
            
            # ===================================================================
            # TABLE 3: STATUS CHECKS
            # ===================================================================
            result = conn.execute(text("""
                SELECT 
                    id,
                    ticket_id,
                    phone_number,
                    checked_at,
                    call_id
                FROM status_checks 
                ORDER BY checked_at DESC 
                LIMIT 50
            """))
            
            rows = result.fetchall()
            columns = result.keys()
            print_table("STATUS CHECKS (Recent 50)", rows, columns)
            
            # ===================================================================
            # TABLE 4: ESCALATIONS
            # ===================================================================
            result = conn.execute(text("""
                SELECT 
                    id,
                    ticket_id,
                    LEFT(reason, 50) as reason,
                    escalated_by,
                    escalated_at,
                    escalated_to,
                    call_id
                FROM escalations 
                ORDER BY escalated_at DESC 
                LIMIT 50
            """))
            
            rows = result.fetchall()
            columns = result.keys()
            print_table("ESCALATIONS (Recent 50)", rows, columns)
            
            # ===================================================================
            # TABLE 5: FEEDBACK
            # ===================================================================
            result = conn.execute(text("""
                SELECT 
                    id,
                    ticket_id,
                    rating,
                    LEFT(feedback_text, 50) as feedback_text,
                    phone_number,
                    submitted_at,
                    call_id
                FROM feedback 
                ORDER BY submitted_at DESC 
                LIMIT 50
            """))
            
            rows = result.fetchall()
            columns = result.keys()
            print_table("FEEDBACK (Recent 50)", rows, columns)
            
            # ===================================================================
            # TABLE 6: EMERGENCIES
            # ===================================================================
            result = conn.execute(text("""
                SELECT 
                    id,
                    emergency_type,
                    location,
                    phone_number,
                    LEFT(description, 50) as description,
                    status,
                    created_at,
                    responded_at,
                    call_id
                FROM emergencies 
                ORDER BY created_at DESC 
                LIMIT 50
            """))
            
            rows = result.fetchall()
            columns = result.keys()
            print_table("EMERGENCIES (Recent 50)", rows, columns)
            
            # ===================================================================
            # SUMMARY STATISTICS
            # ===================================================================
            print(f"\n{'='*120}")
            print("📈 SUMMARY STATISTICS")
            print(f"{'='*120}")
            
            # Count all tables
            tables_count = [
                ("Grievances", "grievances"),
                ("Area Hotspots", "area_hotspots"),
                ("Status Checks", "status_checks"),
                ("Escalations", "escalations"),
                ("Feedback", "feedback"),
                ("Emergencies", "emergencies")
            ]
            
            print(f"\n{'Table':<20} {'Count':<10}")
            print("-" * 30)
            
            for table_name, table in tables_count:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"{table_name:<20} {count:<10}")
            
            # Language distribution
            print(f"\n{'='*120}")
            print("🌍 LANGUAGE DISTRIBUTION")
            print(f"{'='*120}")
            
            result = conn.execute(text("""
                SELECT language, COUNT(*) as count
                FROM grievances
                GROUP BY language
                ORDER BY count DESC
            """))
            
            print(f"\n{'Language':<20} {'Count':<10}")
            print("-" * 30)
            for row in result:
                lang = row[0] or 'unknown'
                count = row[1]
                print(f"{lang:<20} {count:<10}")
            
            # Priority distribution
            print(f"\n{'='*120}")
            print("⚡ PRIORITY DISTRIBUTION")
            print(f"{'='*120}")
            
            result = conn.execute(text("""
                SELECT priority, COUNT(*) as count
                FROM grievances
                GROUP BY priority
                ORDER BY 
                    CASE priority 
                        WHEN 'Critical' THEN 1 
                        WHEN 'High' THEN 2 
                        WHEN 'Medium' THEN 3 
                        WHEN 'Low' THEN 4 
                    END
            """))
            
            print(f"\n{'Priority':<20} {'Count':<10}")
            print("-" * 30)
            for row in result:
                priority = row[0] or 'unknown'
                count = row[1]
                emoji = {
                    'Critical': '🚨',
                    'High': '⚠️',
                    'Medium': '📊',
                    'Low': '📋'
                }.get(priority, '❓')
                print(f"{emoji} {priority:<17} {count:<10}")
            
            # Category distribution
            print(f"\n{'='*120}")
            print("📂 TOP 10 CATEGORIES")
            print(f"{'='*120}")
            
            result = conn.execute(text("""
                SELECT category, COUNT(*) as count
                FROM grievances
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """))
            
            print(f"\n{'Category':<30} {'Count':<10}")
            print("-" * 40)
            for row in result:
                category = row[0] or 'unknown'
                count = row[1]
                print(f"{category:<30} {count:<10}")
            
            # Hotspot status
            print(f"\n{'='*120}")
            print("🔥 HOTSPOT STATUS")
            print(f"{'='*120}")
            
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_areas,
                    SUM(CASE WHEN is_hotspot THEN 1 ELSE 0 END) as flagged_areas,
                    MAX(open_complaints) as max_complaints
                FROM area_hotspots
            """))
            
            row = result.fetchone()
            total_areas = row[0]
            flagged = row[1] or 0
            max_complaints = row[2] or 0
            
            print(f"\nTotal areas tracked:     {total_areas}")
            print(f"Flagged as hotspots:     {flagged}")
            print(f"Max complaints in area:  {max_complaints}")
            
            if flagged > 0:
                result = conn.execute(text("""
                    SELECT area_name, open_complaints, hotspot_level
                    FROM area_hotspots
                    WHERE is_hotspot = TRUE
                    ORDER BY open_complaints DESC
                    LIMIT 10
                """))
                
                print(f"\n🚨 FLAGGED HOTSPOTS:")
                print(f"{'Area':<40} {'Complaints':<15} {'Level':<15}")
                print("-" * 70)
                
                for row in result:
                    area = row[0]
                    count = row[1]
                    level = row[2]
                    emoji = {
                        'CRITICAL': '🔴',
                        'WARNING': '🟡',
                        'SEVERE': '🟣'
                    }.get(level, '⚪')
                    print(f"{area:<40} {count:<15} {emoji} {level:<12}")
            
            print(f"\n{'='*120}")
            print("✅ DATABASE VIEW COMPLETE")
            print(f"{'='*120}\n")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    view_all_tables()
