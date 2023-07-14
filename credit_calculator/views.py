from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login, logout
from django.views.generic import TemplateView
from .forms import SignUpForm
from .forms import CourseSearchForm
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .models import Course, CourseSchedule, UserProfile, Timetable, CourseProfessor, Genre
from django.db.models import Sum


def display_credit(request):
    genres = Genre.objects.all()
    timetables = Timetable.objects.all()

    genre_course_counts = []
    credit_total = 0
    difference_total = 0
    minimum_total = 0
    for genre in genres:
        minimum_total += genre.credit_minimum
        course_count = CourseSchedule.objects.filter(course__genre=genre, timetable__isnull=False).count()
        credit_sum = genre.courses.filter(schedules__timetable__isnull=False).aggregate(total_credits=Sum('credit_number')).get('total_credits')
        credit_sum = 0 if credit_sum is None else credit_sum
        credit_total += credit_sum
        difference =  credit_sum - genre.credit_minimum
        if difference > 0:
            difference = 0
        difference_total = credit_total - minimum_total
        genre_course_counts.append({
            'genre': genre,
            'course_count': course_count,
            'name': genre.name,
            'credit_minimum': genre.credit_minimum,
            'sum': credit_sum,
            'credit_total': credit_total,
            'difference': difference,
            'difference_total': difference_total,
            'minimum_total': minimum_total
        })

    context = {
        'genres': genres,
        'timetables': timetables,
        'genres': genre_course_counts,
        'credit_total': credit_total,
        'difference_total': difference_total,
        'minimum_total': minimum_total
    }

    return render(request, 'display_credit.html', context)

def register_timetable(request):
    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        course_id = request.POST.get('course_id')
        grade = int(request.POST.get('grade'))
        semester = int(request.POST.get('semester'))
        course_instance = get_object_or_404(CourseSchedule, pk=course_id)

        if grade < course_instance.course.minimum_grade_level:
            return JsonResponse({'status':'error', 'message':'受講可能な学年ではありません。'})
        if ("前期" if semester==1 else "後期") != course_instance.semester:
            return JsonResponse({'status':'error', 'message':f'{course_instance.course.name}学期が異なります。'})
        if Timetable.objects.filter(user=user_profile, course_instance__course=course_instance.course).exists():
            return JsonResponse({'status':'error', 'message':course_instance.course.name+'は既に取っています'})

        existing_course = Timetable.objects.filter(user=user_profile, grade=grade, semester=semester, 
                                                   course_instance__day_of_week=course_instance.day_of_week, 
                                                   course_instance__period=course_instance.period)
        if existing_course.exists():
            existing_course.delete()

        timetable, created = Timetable.objects.get_or_create(user=user_profile,
                                                             course_instance=course_instance,
                                                             grade=grade,
                                                             semester=semester)

        if created:
            return JsonResponse({'status':'success', 'message':f'{course_instance.course.name} を時間割に追加しました。'})
        else:
            return JsonResponse({'status':'warning', 'message':f'{course_instance.course.name} は既に時間割に登録されています。'})



# 時間割画面の元をレンダリングするだけ
def timetable(request):return render(request, 'timetable.html')

# 時間割表示の機能
def display_timetable(request):
    grade = int(request.POST.get('grade')) if request.method == 'POST' else 1
    semester = int(request.POST.get('semester')) if request.method == 'POST' else 1
    user_profile = UserProfile.objects.get(user=request.user)

    days = ["月","火","水","木","金","土"]
    periods = list(range(1,7))

    # そのユーザーが指定した学年・学期における時間割情報を取得
    courses = Timetable.objects.filter(user=user_profile, 
                                      grade=grade, 
                                      semester=semester)

    courses_dict = {}
    for i in days:
        for j in periods:
            key = f"{i}{j}"
            try:
                # 特定の曜日・時限に何か授業を取っていれば辞書に格納
                course = courses.get(course_instance__day_of_week=i, course_instance__period=j)
                course_profs = CourseProfessor.objects.filter(course_schedule=course.course_instance).select_related('professor')
                courses_dict[key] = {
                    "name": course.course_instance.course.name,
                    "prof": [f"{prof.professor.last_name} {prof.professor.first_name}" for prof in course_profs],
                    "classroom": course.course_instance.classroom,
                    "genre": course.course_instance.course.genre.name,
                }
            # 特定の曜日・時限に何か授業を取っていなければ辞書には空白を格納
            except Timetable.DoesNotExist:
                courses_dict[key] = {
                    "name": " ",
                    "prof": " ",
                    "classroom": " ",
                    "genre": " ",
                }

    return JsonResponse({'status':'success', 'courses': courses_dict})

# 受講可能な授業のリストを返す（関数名変更したほうがいいかも）
def show_courses(request):
    if request.method == 'POST':
        grade = int(request.POST.get('grade'))
        semester = "前期" if (int(request.POST.get('semester')) == 1) else "後期"
        day = request.POST.get('day')
        period = int(request.POST.get('period'))

        courses = CourseSchedule.objects.filter(course__minimum_grade_level__lte=grade, 
                                                semester=semester, 
                                                day_of_week=day, 
                                                period=period)

        courses_list = []
        for course in courses:
            course_dict = model_to_dict(course)
            course_dict["course_name"] = course.course.name
            course_dict["course_genre"] = course.course.genre.name
            course_profs = CourseProfessor.objects.filter(course_schedule=course).select_related('professor')
            course_dict["course_prof"] = [f"{prof.professor.last_name} {prof.professor.first_name}" for prof in course_profs]
            courses_list.append(course_dict)

        return JsonResponse({'status':'success', 'courses': courses_list})

# 授業を検索する
def course_search(request):
    form = CourseSearchForm(request.GET)
    #フォームが入力されているとき（検索において学期、学年、教授名などが指定されているとき）
    if form.is_valid():
        schedules = CourseSchedule.objects.all()

        semester = form.cleaned_data['semester']
        grade_level = form.cleaned_data['grade_level']
        professor_name = form.cleaned_data['professor_name']

        period_data = {
            CourseSchedule.MONDAY: form.cleaned_data['monday_period'],
            CourseSchedule.TUESDAY: form.cleaned_data['tuesday_period'],
            CourseSchedule.WEDNESDAY: form.cleaned_data['wednesday_period'],
            CourseSchedule.THURSDAY: form.cleaned_data['thursday_period'],
            CourseSchedule.FRIDAY: form.cleaned_data['friday_period'],
            CourseSchedule.SATURDAY: form.cleaned_data['saturday_period'],
        }

        s_objects = Q()
        if semester:
            for s in semester:
                s_objects |= Q(semester=s)
            schedules = schedules.filter(s_objects)
        if grade_level:
            schedules = schedules.filter(course__minimum_grade_level__lte=grade_level)
        if professor_name:
            schedules = schedules.filter(professors__professor__last_name__icontains=professor_name)

        q_objects = Q()
        for day, periods in period_data.items():
            if periods:
                q_objects |= Q(day_of_week=day, period__in=periods)

        schedules = schedules.filter(q_objects)

    return render(request, 'search.html', {'form': form, 'schedules': schedules, 'semester':semester, 'grade_level':grade_level, 'day_and_hour':period_data.items()})

class HomeView(View):
    def get(self, request):
        return render(request, '../templates/home.html', {
            'CourseSchedule': CourseSchedule,
        })

# アカウント作成
def signup_func(request):
    form = SignUpForm
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            
            #from.cleaned_data.getでフォームの入力値を取得
            lastName = form.cleaned_data.get("last_name")
            firstName = form.cleaned_data.get("first_name")

            #バリデート後にusernameをlast_nameとfirst_nameを結合して作成
            username = lastName + " " +firstName
            eMail = form.cleaned_data.get("email")

            # ユーザーを仮設定、パスワードは下でセットするのでここでは仮のパスワードを設定
            new_user = User(username=username, last_name=lastName, first_name=firstName, email=eMail,password="default_password")

            #パスワードをセット
            new_user.set_password(form.cleaned_data.get("password1"))

            #新しいユーザーを
            new_user.save()

            return redirect("signin")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

# サインイン
def signin_func(request):
    if request.method == "POST":

        eMail = request.POST["email"]
        passWord = request.POST["password"]

        print(eMail)
        print(passWord)

        #本来はuser = authenticate()とするのが良いが、email認証だと機能しなかった。
        try:
            user = User.objects.get(email=eMail)
            print("メールアドレスが一致するユーザーを確認しました。")
        except:
            print("メールアドレスが一致するユーザーを確認できませんでした")
            return render (request, "signin.html", {"message":"メールアドレス、またはパズワードが間違っています"})
        
        # メールアドレスが一致するUserを取得した時のみここを通過する

        if check_password(passWord, user.password):
            login(request, user)
            print("ログイン完了！！！")
            return redirect("home")
        else:
            print("パスワードが一致しない")
            return render (request, "signin.html", {"message":"メールアドレス、またはパズワードが間違っています"})
                
    else:
        return render(request, 'signin.html')

#　サインアウト
def signout_func(request):
    logout(request)
    return redirect('home')


class MyPage(TemplateView):
    
    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        return render(request, '../templates/mypage.html', {
            'profile': profile,
        })
    template_name = "mypage.html"
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        profile = UserProfile.objects.get(user=self.request.user)
        grade = profile.grade

        print(profile.user.username)

        if profile.semester == 1:
            semester = "前期"
        elif profile.semester == 2:
            semester = "後期"
        context["grade"] = grade
        context["semester"] = semester
        return context
    
def edit_profile_func(request):
    if request.method == "POST":
        grade = request.POST["grade_select"]
        semester = request.POST["semester_select"]

        print(type(grade))
        print(type(semester))

        profile = UserProfile.objects.get(user=request.user)

        profile.grade = int(grade)
        profile.semester = int(semester)

        profile.save()

        return redirect("mypage")

    return render(request, "edit_profile.html")


#時間割り登録
def new_timetable_item(request, course_id, semester, grade, day_of_week, period, classroom): #semesterはCourseScheduleの持っている値　gradeはCourseのminimum_grade_levelにしてある。詳細が不明だったため間違ってるかも

    if semester == "前期":
        sem = 1
    elif semester == "後期":
        sem = 2

    userProfile = UserProfile.objects.get(user=request.user)

    selected_course = Course.objects.get(id=course_id) #科目の取得

    selected_course_schedule = CourseSchedule.objects.get(course=selected_course, day_of_week=day_of_week, period=period, classroom=classroom) #選択されたCourseScheduleを取得

    # すでに登録されていれば登録はスルー（ただしこのコードでは同じ名前の科目で違う先生、教室などの科目は複数登録できてしまう）
    try:
        t = Timetable.objects.get(user = userProfile, course_instance=selected_course_schedule, grade=grade, semester=sem) # すでに登録されていた場合exceptはスキップされる
        message = "すでに登録されています"
    except:
        timetable = Timetable(user = userProfile, course_instance=selected_course_schedule, grade=grade, semester=sem) # まだ登録されていなかった場合はここで登録される
        timetable.save()
        message = "登録されました！！！"
        
    return HttpResponse(message) #コースのIDを画面に出力
