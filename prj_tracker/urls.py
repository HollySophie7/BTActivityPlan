from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Project URLs
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/create/', ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/update/', ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project-delete'),
    
    # Projects Timeline URL
    path('projects/timeline/', ProjectsTimelineView.as_view(), name='projects-timeline'),

    # Projects Statics URL
    path('projects/statistics/', ProjectStatisticsView.as_view(), name='projects-statistics'),
    
    # UserProfile URLs
    path('team/', UserProfileListView.as_view(), name='userprofile-list'),
    path('team/<int:pk>/', UserProfileDetailView.as_view(), name='userprofile-detail'),
    path('team/create/', UserProfileCreateView.as_view(), name='userprofile-create'),
    path('team/<int:pk>/update/', UserProfileUpdateView.as_view(), name='userprofile-update'),
    path('team/<int:pk>/delete/', UserProfileDeleteView.as_view(), name='userprofile-delete'),
    
    # Division URLs
    path('divisions/', DivisionListView.as_view(), name='division-list'),
    path('divisions/<int:pk>/', DivisionDetailView.as_view(), name='division-detail'),
    path('divisions/create/', DivisionCreateView.as_view(), name='division-create'),
    path('divisions/<int:pk>/update/', DivisionUpdateView.as_view(), name='division-update'),
    path('divisions/<int:pk>/delete/', DivisionDeleteView.as_view(), name='division-delete'),

    # BeneficiaryDivision URLs
    path('beneficiary-divisions/', BeneficiaryDivisionListView.as_view(), name='beneficiarydiv'),
    path('beneficiary-divisions/<int:pk>/', BeneficiaryDivisionDetailView.as_view(), name='beneficiarydiv-detail'),
    path('beneficiary-divisions/create/', BeneficiaryDivisionCreateView.as_view(), name='beneficiarydiv-create'),
    path('beneficiary-divisions/<int:pk>/update/', BeneficiaryDivisionUpdateView.as_view(), name='beneficiarydiv-update'),
    path('beneficiary-divisions/<int:pk>/delete/', BeneficiaryDivisionDeleteView.as_view(), name='beneficiarydiv-delete'),
    
    # YearlyPlan URLs
    path('yearly-plans/', YearlyPlanListView.as_view(), name='yearlyplan-list'),
    path('yearly-plans/<int:pk>/', YearlyPlanDetailView.as_view(), name='yearlyplan-detail'),
    path('yearly-plans/create/', YearlyPlanCreateView.as_view(), name='yearlyplan-create'),
    path('yearly-plans/<int:pk>/update/', YearlyPlanUpdateView.as_view(), name='yearlyplan-update'),
    path('yearly-plans/<int:pk>/delete/', YearlyPlanDeleteView.as_view(), name='yearlyplan-delete'),

    # Perspectives 
    path('perspectives/', PerspectiveListView.as_view(), name='perspective-list'),
    path('perspectives/<int:pk>/', PerspectiveDetailView.as_view(), name='perspective-detail'),
    path('perspectives/create/', PerspectiveCreateView.as_view(), name='perspective-create'),
    path('perspectives/<int:pk>/update/', PerspectiveUpdateView.as_view(), name='perspective-update'),
    path('perspectives/<int:pk>/delete/', PerspectiveDeleteView.as_view(), name='perspective-delete'),
    
    # StrategicObjective URLs
    path('strategic-objectives/', StrategicObjectiveListView.as_view(), name='strategicobjective-list'),
    path('strategic-objectives/<int:pk>/', StrategicObjectiveDetailView.as_view(), name='strategicobjective-detail'),
    path('strategic-objectives/create/', StrategicObjectiveCreateView.as_view(), name='strategicobjective-create'),
    path('strategic-objectives/<int:pk>/update/', StrategicObjectiveUpdateView.as_view(), name='strategicobjective-update'),
    path('strategic-objectives/<int:pk>/delete/', StrategicObjectiveDeleteView.as_view(), name='strategicobjective-delete'),
    
    # StrategicInitiative URLs
    path('strategic-initiatives/', StrategicInitiativeListView.as_view(), name='strategicinitiative-list'),
    path('strategic-initiatives/<int:pk>/', StrategicInitiativeDetailView.as_view(), name='strategicinitiative-detail'),
    path('strategic-initiatives/create/', StrategicInitiativeCreateView.as_view(), name='strategicinitiative-create'),
    path('strategic-initiatives/<int:pk>/update/', StrategicInitiativeUpdateView.as_view(), name='strategicinitiative-update'),
    path('strategic-initiatives/<int:pk>/delete/', StrategicInitiativeDeleteView.as_view(), name='strategicinitiative-delete'),
    
    # ProjectProgress URLs
    path('project-progress/', ProjectProgressListView.as_view(), name='projectprogress-list'),
    path('project-progress/<int:pk>/', ProjectProgressDetailView.as_view(), name='projectprogress-detail'),
    path('project-progress/create/', ProjectProgressCreateView.as_view(), name='projectprogress-create'),
    path('project-progress/<int:pk>/update/', ProjectProgressUpdateView.as_view(), name='projectprogress-update'),
    path('project-progress/<int:pk>/delete/', ProjectProgressDeleteView.as_view(), name='projectprogress-delete'),
    
    # AuditLog URLs (Read-only)
    path('audit-logs/', AuditLogListView.as_view(), name='auditlog-list'),
]