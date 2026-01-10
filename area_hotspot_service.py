"""
Area Hotspot Tracking Service
Automatically detects and flags areas with high complaint density
"""
import re
from sqlalchemy import text
from app.db import engine
from datetime import datetime


def normalize_area_name(area: str) -> str:
    """
    Normalize area names to group similar areas together.
    Example: "Rohini Sector 7", "rohini sector-7", "Rohini Sec 7" → "rohini sector 7"
    """
    if not area:
        return "unknown"
    
    # Convert to lowercase
    normalized = area.lower().strip()
    
    # Remove special characters except spaces and hyphens
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Replace hyphens with spaces
    normalized = normalized.replace('-', ' ')
    
    # Standardize common abbreviations
    replacements = {
        ' sec ': ' sector ',
        ' blk ': ' block ',
        ' st ': ' street ',
        ' rd ': ' road ',
        ' mkt ': ' market ',
    }
    
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    return normalized.strip()


def update_area_hotspot(area: str, category: str, priority: str):
    """
    Update area hotspot statistics when a new complaint is registered.
    This should be called every time a complaint is created.
    """
    if not area:
        return
    
    normalized_area = normalize_area_name(area)
    
    try:
        with engine.begin() as conn:
            # Check if area exists in hotspots table
            result = conn.execute(
                text("SELECT id FROM area_hotspots WHERE normalized_name = :area"),
                {"area": normalized_area}
            )
            
            exists = result.fetchone()
            
            if not exists:
                # Create new area entry
                conn.execute(
                    text("""
                        INSERT INTO area_hotspots 
                        (area_name, normalized_name, total_complaints, open_complaints,
                         first_complaint_at, last_complaint_at)
                        VALUES (:area, :normalized, 1, 1, NOW(), NOW())
                    """),
                    {"area": area, "normalized": normalized_area}
                )
            else:
                # Update existing area
                # Increment total and open complaints
                update_query = """
                    UPDATE area_hotspots 
                    SET total_complaints = total_complaints + 1,
                        open_complaints = open_complaints + 1,
                        last_complaint_at = NOW(),
                        last_updated = NOW()
                """
                
                # Increment category-specific counter
                category_mapping = {
                    "Water Supply": "water_complaints",
                    "Sewage/Drainage": "water_complaints",
                    "Road Maintenance": "road_complaints",
                    "Pollution": "pollution_complaints",
                    "Power Cut": "electricity_complaints"
                }
                
                category_field = category_mapping.get(category, "other_complaints")
                update_query += f", {category_field} = {category_field} + 1"
                
                # Increment priority-specific counter
                priority_mapping = {
                    "Critical": "critical_complaints",
                    "High": "high_complaints",
                    "Medium": "medium_complaints",
                    "Low": "low_complaints"
                }
                
                priority_field = priority_mapping.get(priority, "medium_complaints")
                update_query += f", {priority_field} = {priority_field} + 1"
                
                update_query += " WHERE normalized_name = :area"
                
                conn.execute(text(update_query), {"area": normalized_area})
            
            # Check if area should be flagged as hotspot
            check_and_flag_hotspot(normalized_area)
            
    except Exception as e:
        print(f"❌ Error updating area hotspot: {e}")


def check_and_flag_hotspot(normalized_area: str):
    """
    Check if an area exceeds thresholds and flag it as a hotspot.
    """
    try:
        with engine.begin() as conn:
            # Get current stats
            result = conn.execute(
                text("""
                    SELECT open_complaints, warning_threshold, 
                           critical_threshold, severe_threshold,
                           is_hotspot
                    FROM area_hotspots 
                    WHERE normalized_name = :area
                """),
                {"area": normalized_area}
            )
            
            stats = result.fetchone()
            if not stats:
                return
            
            open_complaints = stats[0]
            warning_threshold = stats[1]
            critical_threshold = stats[2]
            severe_threshold = stats[3]
            currently_flagged = stats[4]
            
            # Determine hotspot level
            new_level = None
            should_flag = False
            
            if open_complaints >= severe_threshold:
                new_level = "SEVERE"
                should_flag = True
            elif open_complaints >= critical_threshold:
                new_level = "CRITICAL"
                should_flag = True
            elif open_complaints >= warning_threshold:
                new_level = "WARNING"
                should_flag = True
            
            # Update if status changed
            if should_flag and not currently_flagged:
                conn.execute(
                    text("""
                        UPDATE area_hotspots 
                        SET is_hotspot = TRUE,
                            hotspot_level = :level,
                            flagged_at = NOW(),
                            alert_sent = FALSE
                        WHERE normalized_name = :area
                    """),
                    {"level": new_level, "area": normalized_area}
                )
                
                print(f"🚨 HOTSPOT ALERT: {normalized_area} flagged as {new_level}")
                
            elif should_flag and currently_flagged:
                # Update level if it changed
                conn.execute(
                    text("""
                        UPDATE area_hotspots 
                        SET hotspot_level = :level,
                            last_updated = NOW()
                        WHERE normalized_name = :area
                    """),
                    {"level": new_level, "area": normalized_area}
                )
                
            elif not should_flag and currently_flagged:
                # Unflag if complaints dropped below threshold
                conn.execute(
                    text("""
                        UPDATE area_hotspots 
                        SET is_hotspot = FALSE,
                            hotspot_level = NULL,
                            last_updated = NOW()
                        WHERE normalized_name = :area
                    """),
                    {"area": normalized_area}
                )
                
                print(f"✅ HOTSPOT CLEARED: {normalized_area}")
                
    except Exception as e:
        print(f"❌ Error checking hotspot: {e}")


def get_hotspot_alerts():
    """
    Get all areas that need attention (hotspots where alert hasn't been sent).
    This can be used to trigger notifications to managers.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT area_name, normalized_name, open_complaints, 
                           hotspot_level, flagged_at
                    FROM area_hotspots
                    WHERE is_hotspot = TRUE AND alert_sent = FALSE
                    ORDER BY 
                        CASE hotspot_level 
                            WHEN 'SEVERE' THEN 1 
                            WHEN 'CRITICAL' THEN 2 
                            WHEN 'WARNING' THEN 3 
                        END,
                        open_complaints DESC
                """)
            )
            
            alerts = [
                {
                    "area_name": row[0],
                    "normalized_name": row[1],
                    "open_complaints": row[2],
                    "level": row[3],
                    "flagged_at": row[4]
                }
                for row in result
            ]
            
            return alerts
            
    except Exception as e:
        print(f"❌ Error getting hotspot alerts: {e}")
        return []


def mark_alert_sent(normalized_area: str):
    """
    Mark that an alert has been sent for this hotspot.
    """
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE area_hotspots 
                    SET alert_sent = TRUE,
                        alert_sent_at = NOW()
                    WHERE normalized_name = :area
                """),
                {"area": normalized_area}
            )
    except Exception as e:
        print(f"❌ Error marking alert sent: {e}")


def get_area_statistics():
    """
    Get overall area statistics for monitoring.
    """
    try:
        with engine.connect() as conn:
            # Total areas tracked
            result = conn.execute(text("SELECT COUNT(*) FROM area_hotspots"))
            total_areas = result.fetchone()[0]
            
            # Hotspot breakdown
            result = conn.execute(
                text("""
                    SELECT hotspot_level, COUNT(*) 
                    FROM area_hotspots 
                    WHERE is_hotspot = TRUE 
                    GROUP BY hotspot_level
                """)
            )
            hotspot_breakdown = {row[0]: row[1] for row in result}
            
            # Top 10 areas by complaint count
            result = conn.execute(
                text("""
                    SELECT area_name, open_complaints, is_hotspot, hotspot_level
                    FROM area_hotspots 
                    ORDER BY open_complaints DESC 
                    LIMIT 10
                """)
            )
            top_areas = [
                {
                    "area": row[0],
                    "open_complaints": row[1],
                    "is_hotspot": row[2],
                    "level": row[3]
                }
                for row in result
            ]
            
            return {
                "total_areas_tracked": total_areas,
                "hotspot_breakdown": hotspot_breakdown,
                "top_problem_areas": top_areas
            }
            
    except Exception as e:
        print(f"❌ Error getting area statistics: {e}")
        return {}


# Example usage in complaint registration:
# from app.services.area_hotspot import update_area_hotspot
# update_area_hotspot(location, category, priority)
