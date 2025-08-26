from django.forms import ModelForm
from .models import *
from django import forms

class YearlyPlanForm(ModelForm):
    class Meta:
        model = YearlyPlan
        fields = ['name', 'description', 'weightage', 'division']
        widgets = {
            'division': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['division'].queryset = Division.objects.all()

class DivisionForm(ModelForm):
    class Meta:
        model = Division
        fields = ['name', 'leader']

        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'})
        }

class PerspectiveForm(ModelForm):
    class Meta:
        model = Perspective
        fields = ['name', 'yearly_plan']

class StrategicObjectiveForm(ModelForm):
    class Meta:
        model = StrategicObjective
        fields = ['strategic_objective_name']


class StrategicInitiativeForm(ModelForm):
    class Meta:
        model = StrategicInitiative
        fields = [
            "strategic_objective", "strategic_initiative_name", "perspective", "responsible_person", "start_date", "end_date", "performance_measure"
        ]

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "project_name", "developer", "system_analyst", "start_date", "end_date", "status", "strategic_initiative", "beneficiary_division_section"
        ]


class BeneficiaryDivisionSectionForm(ModelForm):
    class Meta:
        model = BeneficiaryDivisionSection
        fields = ['name']


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'availability_status', 'specialization']