from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    Project, UserProfile, StrategicObjective, Division, YearlyPlan,
    Perspective, StrategicInitiative, ProjectProgress, AuditLog
)

from .forms import *

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic project statistics
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status__in=['incoming', 'in progress']).count()
        completed_projects = Project.objects.filter(status='completed').count()
        
        # Calculate overdue projects (past end_date and not completed)
        today = timezone.now().date()
        overdue_projects = Project.objects.filter(
            end_date__lt=today,
            status__in=['incoming', 'in progress', 'delayed']
        ).count()
        
        # Project status color distribution
        green_projects = Project.objects.filter().count()
        amber_projects = Project.objects.filter().count()
        brown_projects = Project.objects.filter().count()
        red_projects = Project.objects.filter().count()
        not_started_projects = Project.objects.filter().count()
        
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
            status__in=['incoming', 'in progress']
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

class ProjectProgressCreateView(LoginRequiredMixin, CreateView):
    model = ProjectProgress
    template_name = 'projectprogress/projectprogress_form.html'
    fields = ['project', 'month', 'year', 'status', 'notes']
    success_url = reverse_lazy('projectprogress-list')

class ProjectProgressUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectProgress
    template_name = 'projectprogress/projectprogress_form.html'
    fields = ['project', 'month', 'year', 'status', 'notes']
    success_url = reverse_lazy('projectprogress-list')

class ProjectProgressDeleteView(LoginRequiredMixin, DeleteView):
    model = ProjectProgress
    template_name = 'projectprogress/projectprogress_confirm_delete.html'
    success_url = reverse_lazy('projectprogress-list')

# AuditLog ListView (Read-only for security)
class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'auditlogs/auditlog_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    ordering = ['-timestamp']