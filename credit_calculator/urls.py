from django.urls import path
from . import views
from .views import HomeView, signup_func, signin_func, signout_func, MyPage, course_search, new_timetable_item, display_credit, edit_profile_func

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', signup_func, name="signup"),
    path('signin/', signin_func, name="signin"),
    path('signout/', signout_func, name="signout"),
    path('mypage/', MyPage.as_view(), name="mypage"),
    path('search/', course_search, name='course_search'),
    path('timetable/', views.timetable, name='timetable'),
    path('display_timetable/', views.display_timetable, name='display_timetable'),
    path('register_timetable/', views.register_timetable, name='register_timetable'),
    path('show_courses/', views.show_courses, name='show_courses'),
    path('display_credit/', views.display_credit, name="display_calculator"),

    path('edit_profile.html', edit_profile_func, name="edit_profile"),
]