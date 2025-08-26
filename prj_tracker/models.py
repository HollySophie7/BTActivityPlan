from django.db import models 
from django.contrib.auth.models import User

class Project(models.Model):
    STATUS_CHOICES = [
        ('incoming', 'Incoming'),
        ('in progress', 'In Progress'), 
        ('outgoing', 'Outgoing'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),  
    ]
    
    project_name = models.CharField(max_length=100)
    developer = models.CharField(max_length=100, blank=True, null=True)
    system_analyst = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    progress = models.DecimalField(decimal_places=2, max_digits=4, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responsible_person = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    beneficiary_division = models.CharField(max_length=255, null=True, blank=True)
    strategic_objective = models.ForeignKey('StrategicObjective', on_delete=models.SET_NULL, null=True, blank=True)
    strategic_initiatives_or_activities = models.ForeignKey('StrategicInitiative', on_delete=models.SET_NULL, null=True, blank=True)
    yearly_plan = models.ForeignKey('YearlyPlan', on_delete=models.CASCADE, related_name='projects')
    performance_measure = models.TextField(blank=True, null=True)
    quarterly_status = models.JSONField(default=dict, blank=True)  # Q1, Q2, Q3, Q4 status
    monthly_progress = models.JSONField(default=dict, blank=True)  #
    # lead_developer = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='dev_projects')
    # business_analyst = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='ba_projects')

    COLOR_CHOICES = [
        ('not_started', 'Not Started'),
        ('green', 'Green - On Schedule'),
        ('amber', 'Amber - Partly on Schedule'),
        ('brown', 'Brown - Almost off Schedule'),
        ('red', 'Red - Out of Schedule'),
    ]
    color_status = models.CharField(max_length=20, choices=COLOR_CHOICES, default='not_started')

    def __str__(self):
        return self.project_name
    
class ProjectProgress(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='progress_tracking')
    month = models.CharField(max_length=3, choices=[
        ('Jan', 'January'), ('Feb', 'February'), ('Mar', 'March'),
        ('Apr', 'April'), ('May', 'May'), ('Jun', 'June'),
        ('Jul', 'July'), ('Aug', 'August'), ('Sep', 'September'),
        ('Oct', 'October'), ('Nov', 'November'), ('Dec', 'December')
    ])
    year = models.IntegerField(default=2025)
    status = models.CharField(max_length=20, choices=Project.COLOR_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    ROLES = (
        (1, 'Project Admin'),
        (2, 'Project Officer'),
        (3, 'System Admin'),
        (4, 'Project Manager'),
        (5, 'Developer'),
        (6, 'Business Analyst'),
        (7, 'Technical Lead'),
    )
    
    AVAILABILITY_STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('overloaded', 'Overloaded'),
        ('on_leave', 'On Leave'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="User")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    role = models.IntegerField(choices=ROLES, null=True)
    availability_status = models.CharField(max_length=100, blank=True, null=True)
    responsible_person = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, blank=True)
    current_projects_count = models.IntegerField(default=0)
    specialization = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.role}'
    
class YearlyPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)  
    description = models.TextField(null=True, blank=True)
    weightage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    division = models.ForeignKey('Division', on_delete=models.CASCADE, related_name='yearly_plans', null=True, blank=True)

    def __str__(self):
        return self.name

class Perspective(models.Model):
    PERSPECTIVE_CHOICES = [
        ('financial', 'Financial'),
        ('customer', 'Customer'),
        ('internal_processes', 'Internal Processes'),
        ('innovation_learning_growth', 'Innovation, Learning and Growth'),
        ('sustainability_esg', 'Sustainability and ESG'),
    ]
    
    name = models.CharField(max_length=100, choices=PERSPECTIVE_CHOICES, default='financial')  
    yearly_plan = models.ForeignKey(YearlyPlan, on_delete=models.CASCADE, related_name='perspectives')

    def __str__(self):
        return f"{self.name} - {self.yearly_plan.name}"

class StrategicObjective(models.Model):
    strategic_objective_name = models.CharField(max_length=512, blank=True, null=True)
    
    def __str__(self):
        return f"{self.strategic_objective}"
    
class StrategicInitiative(models.Model):
    strategic_objective = models.ForeignKey(StrategicObjective, on_delete=models.CASCADE, related_name='strategic_objective')
    strategic_initiative_name = models.CharField(max_length=512, null=True, blank=True)
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name='perspective')
    responsible_person = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='responsible_person', null=True, blank=True)  
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    performance_measure = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.strategic_initiatives_or_activities}"

class Division(models.Model):
    DIVISION_CHOICES = [
        ('credit', 'Credit'),
        ('ccm', 'Corporate Communications Management'),
        ('bt', 'Business Technology'),
        ('ct', 'Cente Tech'),
        ('btmc', 'BT-Multi Channels'),
        ('bb', 'Business Banking'),
        ('itsd', 'IT Service Delivery'),
        ('legal', 'Legal'),
        ('finance', 'Finance'),
        ('ca', 'Credit Administration'),
        ('hr', 'Human Resource'),
        ('cbo', 'CBO'),
        ('btmis', '	BT-MIS'),
        ('fm', 'Financial Markets'),
        ('rm', 'Retail & Microfinance'),
    ]
    name = models.CharField(max_length=100, choices=DIVISION_CHOICES, unique=True)
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name
    
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

    def __str__(self):
        return f'{self.user} performed {self.action} on {self.model_name}'
 