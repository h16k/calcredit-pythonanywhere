#templateでのフォームを作りやすくしてくれるファイル
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import CourseSchedule, Course, Professor

class DisplayTimetableForm(forms.Form):
    grade_choices = [(i, f'{i}年') for i in range(1, 5)]
    semester_choices = [(1, '前期'), (2, '後期')]
    
    grade = forms.ChoiceField(choices=grade_choices, label='学年')
    semester = forms.ChoiceField(choices=semester_choices, label='学期')


class CourseSearchForm(forms.Form):
    SEMESTER_CHOICES = list(CourseSchedule.TERM_CHOICES)
    DAY_OF_WEEK_CHOICES = [('', '全て')] + list(CourseSchedule.DAY_OF_WEEK_CHOICES)
    GRADE_CHOICES = [(i, i) for i in range(1, 5)]
    PERIOD_CHOICES = [(i, i) for i in range(1, 7)]

    semester = forms.MultipleChoiceField(choices=SEMESTER_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    grade_level = forms.ChoiceField(choices=GRADE_CHOICES, required=False, label="学年")
    professor_name = forms.CharField(max_length=100, required=False, label="教授名")

    monday_period = forms.MultipleChoiceField(choices=PERIOD_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    tuesday_period = forms.MultipleChoiceField(choices=PERIOD_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    wednesday_period = forms.MultipleChoiceField(choices=PERIOD_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    thursday_period = forms.MultipleChoiceField(choices=PERIOD_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    friday_period = forms.MultipleChoiceField(choices=PERIOD_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    saturday_period = forms.MultipleChoiceField(choices=PERIOD_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)



class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True, #必須項目
        # help_text="必須",
        label="First Name",
    )

    last_name = forms.CharField(
        max_length=50,
        required=True, #必須項目
        # help_text="必須",
        label="Last Name",
    )

    email = forms.EmailField(
        max_length=254,
        label='Email Adress'
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")
