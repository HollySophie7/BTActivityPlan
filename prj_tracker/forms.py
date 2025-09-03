from django.forms import ModelForm
from .models import *
from django import forms

class YearlyPlanForm(ModelForm):
    class Meta:
        model = YearlyPlan
        fields = ['name', 'description', 'weightage', 'division']
        widgets = {
            'division': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['division'].queryset = Division.objects.all()

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"

class DivisionForm(ModelForm):
    class Meta:
        model = Division
        fields = ['name', 'leader']


    def __init__(self, *args, **kwargs):
        super(DivisionForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"

class PerspectiveForm(ModelForm):
    class Meta:
        model = Perspective
        fields = ['name', 'yearly_plan']

    def __init__(self, *args, **kwargs):
        super(PerspectiveForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"

class StrategicObjectiveForm(ModelForm):
    class Meta:
        model = StrategicObjective
        fields = ['strategic_objective_name', 'perspective']

    def __init__(self, *args, **kwargs):
        super(StrategicObjectiveForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"

class StrategicInitiativeForm(ModelForm):
    class Meta:
        model = StrategicInitiative
        fields = [
            "strategic_objective", "strategic_initiative_name", "perspective", "responsible_person", "start_date", "end_date", "performance_measure"
        ]

    def __init__(self, *args, **kwargs):
        super(StrategicInitiativeForm, self).__init__(*args, **kwargs)
        self.fields['strategic_objective'].queryset = StrategicObjective.objects.all()

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "project_name", "developer", "system_analyst", "start_date", "end_date", "status", "priority_rate", "strategic_initiative", "beneficiary_division_section"
        ]

        widgets = {
            'developer': forms.Select(attrs={'class': 'form-select'}),
            'system_analyst': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority_rate': forms.Select(attrs={'class': 'form-select'}),
            'strategic_initiative': forms.Select(attrs={'class': 'form-select'}),
            'beneficiary_division_section': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-control"


class BeneficiaryDivisionSectionForm(ModelForm):
    class Meta:
        model = BeneficiaryDivisionSection
        fields = ['name', 'division']

    def __init__(self, *args, **kwargs):
        super(BeneficiaryDivisionSectionForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["user", 'role', 'availability_status', 'specialization']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"

class ProjectProgressForm(ModelForm):
    class Meta:
        model = ProjectProgress
        fields = ['project', 'month', 'year', 'status', 'notes']

    def __init__(self, *args, **kwargs):
        super(ProjectProgressForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.all()
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-control"


class WeeklyProjectUpdateForm(ModelForm):
    class Meta:
        model = WeeklyProjectUpdate
        fields = ['project', 'date', 'notes']

    def __init__(self, *args, **kwargs):
        super(WeeklyProjectUpdateForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.all()
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-control"


class ProjectCommentForm(ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['project', 'comment', 'status']

    def __init__(self, *args, **kwargs):
        super(ProjectCommentForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.all()
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-control"