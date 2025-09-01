from .models import AuditLog
import logging

logger = logging.getLogger(__name__)

def get_client_info(request):
    """Extract client information from request"""
    # Get IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    # Get user agent info
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    # Simple browser detection
    browser = 'Unknown'
    if 'Chrome' in user_agent:
        browser = 'Chrome'
    elif 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Safari' in user_agent:
        browser = 'Safari'
    elif 'Edge' in user_agent:
        browser = 'Edge'
    
    # Simple OS detection
    os = 'Unknown'
    if 'Windows' in user_agent:
        os = 'Windows'
    elif 'Mac' in user_agent:
        os = 'macOS'
    elif 'Linux' in user_agent:
        os = 'Linux'
    elif 'Android' in user_agent:
        os = 'Android'
    elif 'iOS' in user_agent:
        os = 'iOS'
    
    # Simple device detection
    device = 'Desktop'
    if 'Mobile' in user_agent:
        device = 'Mobile'
    elif 'Tablet' in user_agent:
        device = 'Tablet'
    
    return {
        'ip_address': ip_address,
        'browser': browser,
        'device': device,
        'os': os
    }

def create_audit_log(user, action, model_name, object_id, changes, request):
    """Create an audit log entry with error handling"""
    try:
        client_info = get_client_info(request)
        
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            changes=changes,
            **client_info
        )
    except Exception as e:
        # Log the error but don't break the main functionality
        logger.error(f"Failed to create audit log: {e}")

# Audit Mixin for reusability
class AuditMixin:
    """Mixin to add audit logging to views"""
    
    def create_audit_log(self, action, changes=None):
        """Helper method to create audit log"""
        if not changes:
            changes = f"{action} {self.model.__name__}: {getattr(self.object, 'name', self.object)}"
        
        create_audit_log(
            user=self.request.user,
            action=action,
            model_name=self.model.__name__,
            object_id=self.object.pk,
            changes=changes,
            request=self.request
        )
    
    def get_field_changes(self, original, updated, fields_to_track):
        """Compare original and updated objects to track changes"""
        changes = []
        
        for field in fields_to_track:
            if hasattr(original, field) and hasattr(updated, field):
                old_value = getattr(original, field)
                new_value = getattr(updated, field)
                
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' → '{new_value}'")
        
        return "; ".join(changes) if changes else "No significant changes"