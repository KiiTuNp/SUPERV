from datetime import datetime
import logging
import pytz

# Timezone utility functions
def convert_utc_to_organizer_timezone(utc_datetime: datetime, organizer_timezone: str) -> datetime:
    """Convert UTC datetime to organizer's timezone"""
    if not organizer_timezone:
        return utc_datetime
    
    try:
        # Ensure UTC datetime is timezone-aware
        if utc_datetime.tzinfo is None:
            utc_datetime = pytz.utc.localize(utc_datetime)
        elif utc_datetime.tzinfo != pytz.utc:
            utc_datetime = utc_datetime.astimezone(pytz.utc)
        
        # Convert to organizer's timezone
        organizer_tz = pytz.timezone(organizer_timezone)
        return utc_datetime.astimezone(organizer_tz)
    except Exception as e:
        logging.warning(f"Error converting timezone from UTC to {organizer_timezone}: {e}")
        return utc_datetime

def format_datetime_in_organizer_timezone(utc_datetime: datetime, organizer_timezone: str, format_string: str = '%d/%m/%Y à %H:%M') -> str:
    """Format datetime string in organizer's timezone"""
    try:
        converted_datetime = convert_utc_to_organizer_timezone(utc_datetime, organizer_timezone)
        return converted_datetime.strftime(format_string)
    except Exception as e:
        logging.warning(f"Error formatting datetime in timezone {organizer_timezone}: {e}")
        return utc_datetime.strftime(format_string)

def get_current_time_in_organizer_timezone(organizer_timezone: str) -> datetime:
    """Get current time in organizer's timezone"""
    if not organizer_timezone:
        return datetime.now()
    
    try:
        organizer_tz = pytz.timezone(organizer_timezone)
        return datetime.now(organizer_tz)
    except Exception as e:
        logging.warning(f"Error getting current time in timezone {organizer_timezone}: {e}")
        return datetime.now()
