import calendar
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    Project, UserProfile, StrategicObjective, Division, YearlyPlan,
    Perspective, StrategicInitiative, ProjectProgress, AuditLog
)

from .forms import *
from .utils import AuditMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get counts for each status - FIXED VERSION
        status_counts = Project.objects.values('status').annotate(count=Count('status'))
        
        # Initialize counts dictionary with default values
        counts = {
            'incoming_count': 0,
            'in_progress_count': 0,
            'outgoing_count': 0,
            'completed_count': 0,
            'delayed_count': 0,
        }
        
        # Update counts based on database results
        for item in status_counts:
            status = item['status']
            count = item['count']
            
            if status == 'incoming':
                counts['incoming_count'] = count
            elif status == 'in_progress':  # Fixed: was 'in progress' with space
                counts['in_progress_count'] = count
            elif status == 'outgoing':
                counts['outgoing_count'] = count
            elif status == 'completed':
                counts['completed_count'] = count
            elif status == 'delayed':
                counts['delayed_count'] = count
        
        # Calculate total projects
        total_count = sum(counts.values())
        counts['total_count'] = total_count
        
        # Basic project statistics
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status__in=['incoming', 'in_progress']).count()  # Fixed status name
        completed_projects = Project.objects.filter(status='completed').count()
        
        # Calculate overdue projects (past end_date and not completed)
        today = timezone.now().date()
        overdue_projects = Project.objects.filter(
            end_date__lt=today,
            status__in=['incoming', 'in_progress', 'delayed']  # Fixed status name
        ).count()
        
        # Project status color distribution - ADD PROPER FILTERS
        green_projects = Project.objects.filter(status='completed').count()
        amber_projects = Project.objects.filter(status='in_progress').count()
        brown_projects = Project.objects.filter(status='delayed').count()
        red_projects = Project.objects.filter(status='outgoing').count()
        not_started_projects = Project.objects.filter(status='incoming').count()
        
        # Team workload statistics
        total_team = UserProfile.objects.count()
        if total_team > 0:
            available_team = UserProfile.objects.filter(availability_status='available').count()
            busy_team = UserProfile.objects.filter(availability_status='busy').count()
            overloaded_team = UserProfile.objects.filter(availability_status='overloaded').count()
            
            available_percentage = (available_team / total_team) * 100
            busy_percentage = (busy_team / total_team) * 100
            overloaded_percentage = (overloaded_team / total_team) * 100
        else:
            available_team = busy_team = overloaded_team = 0
            available_percentage = busy_percentage = overloaded_percentage = 0
        
        # Recent projects (last 10)
        recent_projects = Project.objects.order_by('-created_at')[:10]
        
        # Upcoming deadlines (next 30 days)
        upcoming_deadline_date = today + timedelta(days=30)
        upcoming_deadlines = Project.objects.filter(
            end_date__gte=today,
            end_date__lte=upcoming_deadline_date,
            status__in=['incoming', 'in_progress']  # Fixed status name
        ).order_by('end_date')[:5]
        
        # Add days remaining for each deadline
        for project in upcoming_deadlines:
            project.days_remaining = (project.end_date - today).days
            if project.days_remaining <= 7:
                project.priority = 'danger'
            elif project.days_remaining <= 14:
                project.priority = 'warning'
            else:
                project.priority = 'info'
        
        # Strategic objectives with completion status
        strategic_objectives = StrategicInitiative.objects.all()[:6]
        for objective in strategic_objectives:
            # Calculate completion percentage based on associated projects
            objective_projects = Project.objects.filter(strategic_initiative=objective)
            if objective_projects.exists():
                total_progress = sum(float(p.progress) for p in objective_projects)
                objective.completion_percentage = total_progress / objective_projects.count()
                objective.projects_count = objective_projects.count()
            else:
                objective.completion_percentage = 0
                objective.projects_count = 0

        # IMPORTANT: Add the counts to context
        context.update(counts)  # This adds all the count variables
        
        context.update({
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'overdue_projects': overdue_projects,
            
            'green_projects': green_projects,
            'amber_projects': amber_projects,
            'brown_projects': brown_projects,
            'red_projects': red_projects,
            'not_started_projects': not_started_projects,
            
            'available_team': available_team,
            'busy_team': busy_team,
            'overloaded_team': overloaded_team,
            'available_percentage': available_percentage,
            'busy_percentage': busy_percentage,
            'overloaded_percentage': overloaded_percentage,
            
            'recent_projects': recent_projects,
            'upcoming_deadlines': upcoming_deadlines,
            'strategic_objectives': strategic_objectives,
        })
        
        return context
    
# Project CRUD Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Project.objects.order_by('-created_at')
        search = self.request.GET.get('search')
        status_filter = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(project_name__icontains=search) |
                Q(developer__username__icontains=search) |
                Q(developer__first_name__icontains=search) |
                Q(developer__last_name__icontains=search) |
                Q(system_analyst__username__icontains=search) |
                Q(system_analyst__first_name__icontains=search) |
                Q(system_analyst__last_name__icontains=search)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    form_class = ProjectForm

    success_url = reverse_lazy('project-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Project created successfully!')
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    form_class = ProjectForm
    success_url = reverse_lazy('project-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('project-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Project deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
class ProjectStatisticsView(LoginRequiredMixin, View):
    """API view to get project statistics for charts"""
    
    def get(self, request):
        current_year = datetime.now().year
        
        # Initialize monthly data
        months = [calendar.month_abbr[i] for i in range(1, 13)]
        outgoing_monthly = []
        completed_monthly = []
        average_progress_monthly = []
        
        for month in range(1, 13):
            # Count outgoing projects for this month
            outgoing_count = Project.objects.filter(
                status='outgoing',
                created_at__year=current_year,
                created_at__month=month
            ).count()
            outgoing_monthly.append(outgoing_count)
            
            # Count completed projects for this month
            completed_count = Project.objects.filter(
                status='completed',
                created_at__year=current_year,
                created_at__month=month
            ).count()
            completed_monthly.append(completed_count)
            
            # Average progress for this month
            month_projects = Project.objects.filter(
                created_at__year=current_year,
                created_at__month=month
            )
            if month_projects.exists():
                avg_progress = month_projects.aggregate(
                    avg=Avg('progress')
                )['avg'] or 0
                average_progress_monthly.append(round(avg_progress, 1))
            else:
                average_progress_monthly.append(0)
        
        return JsonResponse({
            'months': months,
            'outgoing_monthly': outgoing_monthly,
            'completed_monthly': completed_monthly,
            'average_progress_monthly': average_progress_monthly,
            'total_projects': Project.objects.count(),
            'current_year': current_year,
        })    

# UserProfile CRUD Views
class UserProfileListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_list.html'
    context_object_name = 'profiles'
    paginate_by = 20

class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_detail.html'
    context_object_name = 'profile'

class UserProfileCreateView(LoginRequiredMixin, CreateView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_form.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('userprofile-list')

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_form.html'
    form_class = UserProfileForm

    def form_valid(self, form):
        messages.success(self.request, 'User profile updated successfully!')
        return super().form_valid(form)

    success_url = reverse_lazy('userprofile-list')

class UserProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_confirm_delete.html'
    success_url = reverse_lazy('userprofile-list')

# Division CRUD Views
class DivisionListView(LoginRequiredMixin, ListView):
    model = Division
    template_name = 'divisions/division_list.html'
    context_object_name = 'divisions'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'division'
        return context

class DivisionDetailView(LoginRequiredMixin, DetailView):
    model = Division
    template_name = 'divisions/division_detail.html'
    context_object_name = 'division'

class DivisionCreateView(LoginRequiredMixin, CreateView):
    model = Division
    template_name = 'divisions/division_form.html'
    form_class = DivisionForm
    success_url = reverse_lazy('division-list')

class DivisionUpdateView(LoginRequiredMixin, UpdateView):
    model = Division
    template_name = 'divisions/division_form.html'
    form_class = DivisionForm
    success_url = reverse_lazy('division-list')

class DivisionDeleteView(LoginRequiredMixin, DeleteView):
    model = Division
    template_name = 'divisions/division_confirm_delete.html'
    success_url = reverse_lazy('division-list')


#Beneficially Division
class BeneficiaryDivisionListView(LoginRequiredMixin, ListView):
    model = BeneficiaryDivisionSection
    template_name = 'divisions/division_list.html'
    context_object_name = 'divisions'
    paginate_by = 20
    success_url = reverse_lazy('beneficiarydiv')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'beneficiary'
        return context

class BeneficiaryDivisionDetailView(LoginRequiredMixin, DetailView):
    model = BeneficiaryDivisionSection
    template_name = 'divisions/division_detail.html'
    context_object_name = 'division'
    success_url = reverse_lazy('beneficiarydiv')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'beneficiary'
        return context

class BeneficiaryDivisionCreateView(LoginRequiredMixin, CreateView):
    model = BeneficiaryDivisionSection
    template_name = 'divisions/division_form.html'
    form_class = BeneficiaryDivisionSectionForm
    success_url = reverse_lazy('beneficiarydiv')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'beneficiary'
        return context

class BeneficiaryDivisionUpdateView(LoginRequiredMixin, UpdateView):
    model = BeneficiaryDivisionSection
    template_name = 'divisions/division_form.html'
    form_class = BeneficiaryDivisionSectionForm
    success_url = reverse_lazy('beneficiarydiv')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'beneficiary'
        return context

class BeneficiaryDivisionDeleteView(LoginRequiredMixin, DeleteView):
    model = BeneficiaryDivisionSection
    template_name = 'divisions/division_confirm_delete.html'
    success_url = reverse_lazy('beneficiarydiv')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'beneficiary'
        return context

# YearlyPlan CRUD Views
class YearlyPlanListView(LoginRequiredMixin, ListView):
    model = YearlyPlan
    template_name = 'yearlyplans/yearlyplan_list.html'
    context_object_name = 'plans'
    paginate_by = 20

class YearlyPlanDetailView(LoginRequiredMixin, DetailView):
    model = YearlyPlan
    template_name = 'yearlyplans/yearlyplan_detail.html'
    context_object_name = 'plan'

class YearlyPlanCreateView(LoginRequiredMixin, CreateView):
    model = YearlyPlan
    template_name = 'yearlyplans/yearlyplan_form.html'
    form_class = YearlyPlanForm
    success_url = reverse_lazy('yearlyplan-list')

class YearlyPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = YearlyPlan
    template_name = 'yearlyplans/yearlyplan_form.html'
    form_class = YearlyPlanForm
    success_url = reverse_lazy('yearlyplan-list')

class YearlyPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = YearlyPlan
    template_name = 'yearlyplans/yearlyplan_confirm_delete.html'
    success_url = reverse_lazy('yearlyplan-list')


#Perspectives Views 
class PerspectiveListView(LoginRequiredMixin, ListView):
    model = Perspective
    template_name = 'perspectives/perspective_list.html'
    context_object_name = 'perspectives'
    paginate_by = 20

class PerspectiveDetailView(LoginRequiredMixin, DetailView):
    model = Perspective
    template_name = 'perspectives/perspective_detail.html'
    context_object_name = 'perspective'

class PerspectiveCreateView(LoginRequiredMixin, CreateView):
    model = Perspective
    template_name = 'perspectives/perspective_form.html'
    form_class = PerspectiveForm
    success_url = reverse_lazy('perspective-list')

class PerspectiveUpdateView(LoginRequiredMixin, UpdateView):
    model = Perspective
    template_name = 'perspectives/perspective_form.html'
    form_class = PerspectiveForm
    success_url = reverse_lazy('perspective-list')

class PerspectiveDeleteView(LoginRequiredMixin, DeleteView):
    model = Perspective
    template_name = 'perspectives/perspective_confirm_delete.html'
    success_url = reverse_lazy('perspective-list')


# StrategicObjective CRUD Views
class StrategicObjectiveListView(LoginRequiredMixin, ListView):
    model = StrategicObjective
    template_name = 'strategicobjectives/strategicobjective_list.html'
    context_object_name = 'objectives'
    paginate_by = 20

class StrategicObjectiveDetailView(LoginRequiredMixin, DetailView):
    model = StrategicObjective
    template_name = 'strategicobjectives/strategicobjective_detail.html'
    context_object_name = 'objective'

class StrategicObjectiveCreateView(LoginRequiredMixin, CreateView):
    model = StrategicObjective
    template_name = 'strategicobjectives/strategicobjective_form.html'
    form_class = StrategicObjectiveForm
    success_url = reverse_lazy('strategicobjective-list')

class StrategicObjectiveUpdateView(LoginRequiredMixin, UpdateView):
    model = StrategicObjective
    template_name = 'strategicobjectives/strategicobjective_form.html'
    form_class = StrategicObjectiveForm
    success_url = reverse_lazy('strategicobjective-list')

class StrategicObjectiveDeleteView(LoginRequiredMixin, DeleteView):
    model = StrategicObjective
    template_name = 'strategicobjectives/strategicobjective_confirm_delete.html'
    success_url = reverse_lazy('strategicobjective-list')

# StrategicInitiative CRUD Views
class StrategicInitiativeListView(LoginRequiredMixin, ListView):
    model = StrategicInitiative
    template_name = 'strategicinitiatives/strategicinitiative_list.html'
    context_object_name = 'initiatives'
    paginate_by = 20

class StrategicInitiativeDetailView(LoginRequiredMixin, DetailView):
    model = StrategicInitiative
    template_name = 'strategicinitiatives/strategicinitiative_detail.html'
    context_object_name = 'initiative'

class StrategicInitiativeCreateView(LoginRequiredMixin, CreateView):
    model = StrategicInitiative
    template_name = 'strategicinitiatives/strategicinitiative_form.html'
    form_class = StrategicInitiativeForm
    success_url = reverse_lazy('strategicinitiative-list')

class StrategicInitiativeUpdateView(LoginRequiredMixin, UpdateView):
    model = StrategicInitiative
    template_name = 'strategicinitiatives/strategicinitiative_form.html'
    form_class = StrategicInitiativeForm
    success_url = reverse_lazy('strategicinitiative-list')

class StrategicInitiativeDeleteView(LoginRequiredMixin, DeleteView):
    model = StrategicInitiative
    template_name = 'strategicinitiatives/strategicinitiative_confirm_delete.html'
    success_url = reverse_lazy('strategicinitiative-list')

# ProjectProgress CRUD Views
class ProjectProgressListView(LoginRequiredMixin, ListView):
    model = ProjectProgress
    template_name = 'projectprogress/projectprogress_list.html'
    context_object_name = 'progress_entries'
    paginate_by = 20

class ProjectProgressDetailView(LoginRequiredMixin, DetailView):
    model = ProjectProgress
    template_name = 'projectprogress/projectprogress_detail.html'
    context_object_name = 'progress'

class ProjectProgressCreateView(LoginRequiredMixin, CreateView, AuditMixin):
    model = ProjectProgress
    template_name = 'projectprogress/projectprogress_form.html'
    form_class = ProjectProgressForm
    success_url = reverse_lazy('projectprogress-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create audit log
        details = []
        if hasattr(self.object, 'project'):
            details.append(f"Project: {self.object.project}")
        if hasattr(self.object, 'progress_percentage'):
            details.append(f"Progress: {self.object.progress_percentage}%")
        
        changes = f"Created project progress: {'; '.join(details) if details else 'New progress entry'}"
        self.create_audit_log('CREATE', changes)
        
        return response

class ProjectProgressUpdateView(LoginRequiredMixin, UpdateView, AuditMixin):
    model = ProjectProgress
    template_name = 'projectprogress/projectprogress_form.html'
    form_class = ProjectProgressForm
    success_url = reverse_lazy('projectprogress-list')

    def form_valid(self, form):
        # Store the original object for comparison
        original_obj = ProjectProgress.objects.get(pk=self.object.pk)
        
        # Save the form first
        response = super().form_valid(form)
        
        # Create audit log for the update
        fields_to_track = ['progress_percentage', 'status', 'description', 'milestone']
        changes = self.get_field_changes(original_obj, form.instance, fields_to_track)
        
        self.create_audit_log('UPDATE', f"Updated project progress: {changes}")
        
        return response

class ProjectProgressDeleteView(LoginRequiredMixin, DeleteView, AuditMixin):
    model = ProjectProgress
    template_name = 'projectprogress/projectprogress_confirm_delete.html'
    success_url = reverse_lazy('projectprogress-list')

    def delete(self, request, *args, **kwargs):
        # Store object info before deletion
        obj = self.get_object()
        self.object = obj  # Set for the mixin
        
        # Create audit log before deletion
        object_info = f"Progress ID: {obj.pk}"
        if hasattr(obj, 'project'):
            object_info += f", Project: {obj.project}"
        if hasattr(obj, 'progress_percentage'):
            object_info += f", Progress: {obj.progress_percentage}%"
        
        self.create_audit_log('DELETE', f"Deleted project progress: {object_info}")
        
        # Proceed with deletion
        return super().delete(request, *args, **kwargs)



# Projects TimelineView
class ProjectsTimelineView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/projects_timeline.html'

    def get(self, request, *args, **kwargs):
        """Projects Timeline View with cascading filters"""

        # Get all data
        projects = Project.objects.all()
        perspectives = Perspective.objects.all()
        objectives = StrategicObjective.objects.all()
        initiatives = StrategicInitiative.objects.all()

        # Get filter values from GET parameters
        perspective_id = request.GET.get('perspective')
        objective_id = request.GET.get('objective')
        initiative_id = request.GET.get('initiative')


        # Filter initiatives and objectives first
        if perspective_id:
            objectives = objectives.filter(perspective_id=perspective_id)
            initiatives = initiatives.filter(strategic_objective__perspective_id=perspective_id)

        if objective_id:
            initiatives = initiatives.filter(strategic_objective_id=objective_id)
        
        # Filter projects based on the related strategic initiative
        if perspective_id:
            projects = projects.filter(strategic_initiative__strategic_objective__perspective_id=perspective_id)
        
        if objective_id:
            projects = projects.filter(strategic_initiative__strategic_objective_id=objective_id)
        
        if initiative_id:
            projects = projects.filter(strategic_initiative_id=initiative_id)

        # Calculate stats
        stats = {
            'total': projects.count(),
            'completed': projects.filter(status__icontains='completed').count(),
            'in_progress': projects.filter(status__icontains='in_progress').count(),
            'incoming': projects.filter(status__icontains='incoming').count(),
            'delayed': projects.filter(status__icontains='delayed').count(),
            'outgoing': projects.filter(status__icontains='outgoing').count(),
        }

        final_projects = []
        if perspective_id != None or objective_id != None or initiative_id != None:
            print(f'-------XX------>{perspective_id}, {objective_id}, {initiative_id}')
            final_projects = projects

        context = {
            'projects': final_projects,
            'perspectives': perspectives,
            'objectives': objectives,
            'initiatives': initiatives,
            'stats': stats,
        }

        return render(request, 'projects/projects_timeline.html', context)


# AuditLog ListView (Read-only for security)
class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'auditlogs/auditlog_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    ordering = ['-timestamp']