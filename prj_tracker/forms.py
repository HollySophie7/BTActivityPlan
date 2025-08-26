from django.forms import ModelForm
from .models import *

class YearlyPlanForm(ModelForm):
    class Meta:
        model = YearlyPlan
        fields = ['name', 'description', 'weightage', 'division']

class DivisionForm(ModelForm):
    class Meta:
        model = Division
        fields = ['name', 'leader']

class PerspectiveForm(ModelForm):
    class Meta:
        model = Perspective
        fields = ['name', 'description']

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
            'project_name', 'developer', 'system_analyst', 'start_date', 'end_date',
            'progress', 'status', 'responsible_person', 'comments', 'beneficiary_division',
            'strategic_objective', 'strategic_initiatives_or_activities', 'yearly_plan',
            'performance_measure', 'color_status'
        ]
