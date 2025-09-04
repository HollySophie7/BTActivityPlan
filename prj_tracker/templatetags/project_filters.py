from django import template
from datetime import datetime, date
import calendar
import re

register = template.Library()

@register.filter
def is_active_in_month(project, month_num):
    """Check if project is active in the given month (1-12) of 2025"""
    if not project.start_date or not project.end_date:
        return False
    
    try:
        month_num = int(month_num)
        year = 2025  # Your timeline year
        
        # Parse the dates properly
        start_date = parse_date_field(project.start_date)
        end_date = parse_date_field(project.end_date)
        
        if not start_date or not end_date:
            return False
        
        # Create month boundaries
        month_start = date(year, month_num, 1)
        month_end = date(year, month_num, calendar.monthrange(year, month_num)[1])
        
        # Check if project overlaps with this month
        return not (end_date < month_start or start_date > month_end)
        
    except (ValueError, AttributeError, TypeError):
        return False

@register.filter
def get_month_span_info(project, month_num):
    """Get detailed spanning information for a project in a specific month"""
    month = int(month_num)
    year = 2025  # Your timeline year
    
    if not project.start_date or not project.end_date:
        return {'is_active': False}
    
    # Parse the dates properly
    start_date = parse_date_field(project.start_date)
    end_date = parse_date_field(project.end_date)
    
    if not start_date or not end_date:
        return {'is_active': False}
    
    # Month boundaries
    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    
    # Check if project is active in this month
    if end_date < month_start or start_date > month_end:
        return {'is_active': False}
    
    # Determine if this is start/end/middle month
    is_start_month = (start_date.year == year and start_date.month == month)
    is_end_month = (end_date.year == year and end_date.month == month)
    
    # Calculate partial width and positioning
    width_percentage = 100
    margin_left_percentage = 0
    partial_width = False
    
    if is_start_month or is_end_month:
        partial_width = True
        days_in_month = month_end.day
        
        if is_start_month and is_end_month:
            # Project starts and ends in same month
            start_day = start_date.day
            end_day = end_date.day
            width_percentage = ((end_day - start_day + 1) / days_in_month) * 100
            margin_left_percentage = ((start_day - 1) / days_in_month) * 100
        elif is_start_month:
            # Project starts in this month
            start_day = start_date.day
            width_percentage = ((days_in_month - start_day + 1) / days_in_month) * 100
            margin_left_percentage = ((start_day - 1) / days_in_month) * 100
        elif is_end_month:
            # Project ends in this month
            end_day = end_date.day
            width_percentage = (end_day / days_in_month) * 100
            margin_left_percentage = 0
    
    # Calculate progress for active projects
    progress_percentage = 0
    if hasattr(project, 'status') and project.status == 'in_progress':
        today = date.today()
        if month_start <= today <= month_end and start_date <= today:
            total_days = (end_date - start_date).days + 1
            completed_days = (today - start_date).days + 1
            progress_percentage = min((completed_days / total_days) * 100, 100)
    
    return {
        'is_active': True,
        'is_start_month': is_start_month,
        'is_end_month': is_end_month,
        'width_percentage': round(width_percentage, 2),
        'margin_left_percentage': round(margin_left_percentage, 2),
        'partial_width': partial_width,
        'progress_percentage': round(progress_percentage, 2) if progress_percentage > 0 else None
    }

def parse_date_field(date_field):
    """Parse date from various formats and return a date object"""
    if not date_field:
        return None
    
    # If it's already a date or datetime object
    if isinstance(date_field, (date, datetime)):
        if isinstance(date_field, datetime):
            return date_field.date()
        return date_field
    
    # Convert to string for parsing
    date_str = str(date_field).strip()
    
    if not date_str or date_str.lower() in ['none', 'null', '']:
        return None
    
    # Handle "Jan-25", "Feb-25" format
    month_year_pattern = r'^([A-Za-z]{3})-(\d{2})$'
    match = re.match(month_year_pattern, date_str)
    if match:
        month_abbrev, year_short = match.groups()
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
            'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
            'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        month_num = month_map.get(month_abbrev.capitalize())
        if month_num:
            year = 2000 + int(year_short)  # Convert 25 to 2025
            return date(year, month_num, 1)  # Use first day of month
    
    # Handle various date formats
    date_formats = [
        '%Y-%m-%d',      # 2025-01-15
        '%m/%d/%Y',      # 01/15/2025
        '%d/%m/%Y',      # 15/01/2025
        '%Y/%m/%d',      # 2025/01/15
        '%m-%d-%Y',      # 01-15-2025
        '%d-%m-%Y',      # 15-01-2025
        '%b %d, %Y',     # Jan 15, 2025
        '%B %d, %Y',     # January 15, 2025
        '%d %b %Y',      # 15 Jan 2025
        '%d %B %Y',      # 15 January 2025
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.date()
        except ValueError:
            continue
    
    # Try to extract numbers and guess the format
    numbers = re.findall(r'\d+', date_str)
    if len(numbers) >= 2:
        try:
            # If we have 3 numbers, try different combinations
            if len(numbers) == 3:
                num1, num2, num3 = [int(n) for n in numbers]
                
                # Try YYYY-MM-DD
                if num1 > 1900:
                    return date(num1, num2, num3)
                # Try MM/DD/YYYY or DD/MM/YYYY
                elif num3 > 1900:
                    if num1 <= 12 and num2 <= 31:  # MM/DD/YYYY
                        return date(num3, num1, num2)
                    elif num2 <= 12 and num1 <= 31:  # DD/MM/YYYY
                        return date(num3, num2, num1)
            
            # If we have 2 numbers, assume it's month-year
            elif len(numbers) == 2:
                num1, num2 = [int(n) for n in numbers]
                if num2 > 50:  # Assume it's full year
                    year = num2 if num2 > 1900 else 2000 + num2
                    month = num1 if num1 <= 12 else 1
                    return date(year, month, 1)
                elif num1 > 50:  # Assume first is year
                    year = num1 if num1 > 1900 else 2000 + num1
                    month = num2 if num2 <= 12 else 1
                    return date(year, month, 1)
        except (ValueError, TypeError):
            pass
    
    return None

@register.filter
def format_project_date(date_field):
    """Format date for display"""
    parsed_date = parse_date_field(date_field)
    if parsed_date:
        return parsed_date.strftime('%b %d, %Y')
    return 'N/A'

@register.filter
def get_project_duration_days(project):
    """Get project duration in days"""
    if not project.start_date or not project.end_date:
        return 0
    
    start_date = parse_date_field(project.start_date)
    end_date = parse_date_field(project.end_date)
    
    if start_date and end_date:
        return (end_date - start_date).days + 1
    return 0

@register.filter
def is_project_overdue(project):
    """Check if project is overdue"""
    if not project.end_date:
        return False
    
    end_date = parse_date_field(project.end_date)
    if end_date:
        return date.today() > end_date and hasattr(project, 'status') and project.status != 'completed'
    return False

@register.filter
def get_project_progress_percentage(project):
    """Calculate project progress percentage based on dates"""
    if not project.start_date or not project.end_date:
        return 0
    
    start_date = parse_date_field(project.start_date)
    end_date = parse_date_field(project.end_date)
    
    if not start_date or not end_date:
        return 0
    
    today = date.today()
    
    if today < start_date:
        return 0
    elif today > end_date:
        return 100
    else:
        total_days = (end_date - start_date).days + 1
        elapsed_days = (today - start_date).days + 1
        return round((elapsed_days / total_days) * 100, 1)

# Additional utility filters
@register.filter
def sub(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide value by arg"""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """Add arg to value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0