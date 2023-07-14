from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver

# 科目群のモデル
class Genre(models.Model):
    name = models.CharField(max_length=20)  # 科目群の名前
    credit_minimum = models.IntegerField(default=0)  # 最低単位数


# 科目のモデル
class Course(models.Model):
    REQUIRED = 0
    SELECT = 1
    REQUIRED_OR_SELECT_CHOICES = [
        (REQUIRED, 'Required'),
        (SELECT, 'Select'),
    ]

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='courses')  # ジャンルへの参照
    faculty = models.CharField(max_length=20, default='国際情報学部') #学部の名前
    name = models.CharField(max_length=100)  # 科目の名前
    credit_number = models.IntegerField(default=2)  # 単位数
    required_or_select = models.IntegerField(choices=REQUIRED_OR_SELECT_CHOICES)  # 必修科目か選択科目か
    minimum_grade_level = models.IntegerField(default=1)  # 受講可能な最低学年


# 科目のスケジュールのモデル
class CourseSchedule(models.Model):
    FIRST_TERM = "前期"
    SECOND_TERM = "後期"
    SUMMER = "夏季集中"
    ALL_YEAR = "通年"
    TERM_CHOICES = [
        (FIRST_TERM, '前期'),
        (SECOND_TERM, '後期'),
        (SUMMER, '夏季集中'),
        (ALL_YEAR, '通年'),
    ]

    NULL = "なし"
    MONDAY = "月"
    TUESDAY = "火"
    WEDNESDAY = "水"
    THURSDAY = "木"
    FRIDAY = "金"
    SATURDAY = "土"

    DAY_OF_WEEK_CHOICES = [
        (NULL, 'その他'),
        (MONDAY, '月曜'),
        (TUESDAY, '火曜'),
        (WEDNESDAY, '水曜'),
        (THURSDAY, '木曜'),
        (FRIDAY, '金曜'),
        (SATURDAY, '土曜'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')  # 科目への参照
    semester = models.CharField(max_length = 20, choices=TERM_CHOICES, default=FIRST_TERM)
    day_of_week = models.CharField(max_length = 5, choices=DAY_OF_WEEK_CHOICES)  # 曜日
    period = models.IntegerField()  # 時間帯
    classroom = models.CharField(max_length = 50, blank=True) #教室

# 教授のモデル
class Professor(models.Model):
    last_name = models.CharField(max_length = 50)  # 教授の姓
    first_name = models.CharField(max_length = 50)  # 教授の名

# 科目と教授の関連性のモデル
class CourseProfessor(models.Model):
    course_schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE, related_name='professors')  # 科目スケジュールへの参照
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)  # 教授への参照


# ユーザーのプロフィールのモデル
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ユーザーへの参照
    grade = models.IntegerField(default=1, blank=True)  # 現在の学年 
    semester = models.IntegerField(default=1, blank=True)  # 現在の学期　1が前期
    
    #以下のコードでユーザーが作成されるとこのユーザープロフィールモデルも同時で作成されるようになる。
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

# ユーザーのタイムテーブルのモデル
class Timetable(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # ユーザープロフィールへの参照
    course_instance = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)  # 科目のインスタンスへの参照
    grade = models.IntegerField() # その授業を登録した学年 
    semester = models.IntegerField() # その授業を登録した学期 

# ユーザーの「いいね」のモデル
class Like(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # ユーザープロフィールへの参照
    course_instance = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)  # 科目のインスタンスへの参照

# UserのEmailをUniqueにする
User._meta.get_field('email')._unique = True