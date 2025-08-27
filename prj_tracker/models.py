from django.db import models 
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLES = (
        (1, 'Project Admin'),
        (2, 'Project Officer'),
        (3, 'System Admin'),
        (4, 'Project Manager'),
        (5, 'Developer'),
        (6, 'System Analyst'),
    )
    
    AVAILABILITY_STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('overloaded', 'Overloaded'),
        ('on_leave', 'On Leave'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="User")
    role = models.IntegerField(choices=ROLES, null=True)
    availability_status = models.CharField(max_length=100, blank=True, null=True, default='available', choices=AVAILABILITY_STATUS_CHOICES)
    current_projects_count = models.IntegerField(default=0)
    specialization = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.role}'
    
    # TODO: Add a method to update the current_projects_count
    

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)  # Create a UserProfile for the new user
    else:
        # Only save if profile exists (to avoid errors)
        if hasattr(instance, 'profile'):
            instance.profile.save()



class Division(models.Model):
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_name_display(self):
        return self.name
    
    def get_leader(self):
        return self.leader
    
class BeneficiaryDivisionSection(models.Model):
    name = models.CharField(max_length=100, unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='beneficiary_division_sections')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_name_display(self):
        return self.name
    
    def get_leader(self):
        return self.division.leader

    
class YearlyPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)  
    description = models.TextField(null=True, blank=True)
    weightage = models.TextField(null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='yearly_plans', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    

    def __str__(self):
        return self.name

class Perspective(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)  
    yearly_plan = models.ForeignKey(YearlyPlan, on_delete=models.CASCADE, related_name='perspectives')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class StrategicObjective(models.Model):
    strategic_objective_name = models.CharField(max_length=512, blank=True, null=True)
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name='strategic_objective', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.strategic_objective}"
    
class StrategicInitiative(models.Model):
    strategic_objective = models.ForeignKey(StrategicObjective, on_delete=models.CASCADE, related_name='strategic_objective', null=True, blank=True)
    strategic_initiative_name = models.CharField(max_length=512, null=True, blank=True)
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name='perspective', null=True, blank=True)
    responsible_person = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='responsible_person', null=True, blank=True)  
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    performance_measure = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    

    def __str__(self):
        return f"{self.strategic_initiatives_or_activities}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('incoming', 'Incoming'),
        ('in_progress', 'In Progress'), 
        ('outgoing', 'Outgoing'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),  
    ]
    
    project_name = models.CharField(max_length=100)
    developer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dev_projects')
    system_analyst = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='ba_projects', blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    progress = models.DecimalField(decimal_places=2, max_digits=4, default=0.00, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incoming')
    strategic_initiative = models.ForeignKey('StrategicInitiative', on_delete=models.SET_NULL, null=True, blank=True)
    quarterly_status = models.JSONField(default=dict, blank=True)  # Q1, Q2, Q3, Q4 status
    monthly_progress = models.JSONField(default=dict, blank=True)
    beneficiary_division_section = models.ForeignKey(BeneficiaryDivisionSection, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.project_name
    
class ProjectComment(models.Model):
    status_choices = [
        ("open", "Open"),
        ("in_review", "In Review"),
        ("closed", "Closed"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    status = models.CharField(max_length=20, choices=status_choices, default='open')   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WeeklyProjectUpdate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='weekly_updates')
    date = models.DateField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProjectProgress(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='progress_tracking')
    month = models.CharField(max_length=3, choices=[
        ('Jan', 'January'), ('Feb', 'February'), ('Mar', 'March'),
        ('Apr', 'April'), ('May', 'May'), ('Jun', 'June'),
        ('Jul', 'July'), ('Aug', 'August'), ('Sep', 'September'),
        ('Oct', 'October'), ('Nov', 'November'), ('Dec', 'December')
    ])
    year = models.IntegerField(default=2025)
    status = models.CharField(max_length=20, choices=Project.STATUS_CHOICES, default='incoming')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, null=True, blank=True)
    browser = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100, null=True, blank=True)  
    object_id = models.CharField(max_length=100, null=True, blank=True) 
    changes = models.TextField(null=True, blank=True)  
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for device, OS, and IP address
    device = models.CharField(max_length=100, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(max_length=100,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'{self.user} performed {self.action} on {self.model_name}'
 