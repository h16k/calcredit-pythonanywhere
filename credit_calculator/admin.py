from django.contrib import admin

from .models import Genre, Course, CourseSchedule, Professor, CourseProfessor, UserProfile, Timetable, Like

# Register your models here.

admin.site.register(Genre)
admin.site.register(Course)
admin.site.register(CourseSchedule)
admin.site.register(Professor)
admin.site.register(CourseProfessor)
admin.site.register(UserProfile)
admin.site.register(Timetable)
admin.site.register(Like)