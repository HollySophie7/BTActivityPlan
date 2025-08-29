from django import template
from datetime import datetime
import re

register = template.Library()

@register.filter
def is_active_in_month(project, month_num):
    """Check if project is active in the given month (1-12)"""
    if not project.start_date or not project.end_date:
        return False
    
    try:
        month_num = int(month_num)
        
        # Parse dates - handle different formats
        start_month = parse_month_from_date(project.start_date)
        end_month = parse_month_from_date(project.end_date)
        
        if start_month == -1 or end_month == -1:
            return False
            
        return start_month <= month_num <= end_month
        
    except (ValueError, AttributeError):
        return False

def parse_month_from_date(date_field):
    """Parse month from various date formats"""
    if not date_field:
        return -1
    
    date_str = str(date_field)
    
    # Handle datetime objects
    if hasattr(date_field, 'month'):
        return date_field.month
    
    # Handle "Jan-25", "Feb-25" format
    if '-' in date_str and len(date_str.split('-')[0]) == 3:
        month_abbrev = date_str.split('-')[0]
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
            'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
            'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        return month_map.get(month_abbrev, -1)
    
    # Handle standard date formats
    try:
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) >= 2:
                return int(parts[1])  # MM/DD/YYYY
        elif '-' in date_str:
            parts = date_str.split('-')
            if len(parts) >= 2:
                return int(parts[1])  # YYYY-MM-DD
    except (ValueError, IndexError):
        pass
    
    return -1