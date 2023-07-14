from django.core.management.base import BaseCommand
# 先程のスクリプトで使用したモデルのimport文も必要です。

class Command(BaseCommand):
    help = 'Import data from TSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='The filepath of the TSV file')

    def handle(self, *args, **options):
        file_path = options['file']
        register_tsv_data(file_path)  # 先程のスクリプト

import csv
from django.db import transaction
from credit_calculator.models import Genre, Course, Professor, CourseProfessor, CourseSchedule


def register_tsv_data(filepath):
    # 開始日と終了日
    semester_mapping = {
    "前期": CourseSchedule.FIRST_TERM,
    "後期": CourseSchedule.SECOND_TERM,
    "夏季集中": CourseSchedule.SUMMER,
    "通年": CourseSchedule.ALL_YEAR,
    }
    
    # 曜日
    week_days = {
        'NULL': CourseSchedule.NULL,
        '月': CourseSchedule.MONDAY,
        '火': CourseSchedule.TUESDAY,
        '水': CourseSchedule.WEDNESDAY,
        '木': CourseSchedule.THURSDAY,
        '金': CourseSchedule.FRIDAY,
        '土': CourseSchedule.SATURDAY,

    }

    with open(filepath, 'r', encoding='utf-8') as file:
        tsv_reader = csv.reader(file, delimiter='\t')
        with transaction.atomic():  # トランザクションを開始
            for row in tsv_reader:
                print(row)
                genre, _ = Genre.objects.get_or_create(name=row[0], credit_minimum = row[10])
                course, _ = Course.objects.get_or_create(name=row[1], genre=genre, credit_number=row[8], minimum_grade_level=row[7], required_or_select=row[9], faculty = row[11])
                
                course_schedule, _ = CourseSchedule.objects.get_or_create(
                    course=course,
                    semester=semester_mapping[row[2]],
                    day_of_week=week_days[row[3]],
                    period=row[4],
                    classroom=row[5] if row[5] else None
                )

                # 教授が複数いる場合を考慮
                professors = row[6].split('、')
                for prof in professors:
                    last_name, first_name = prof.split('　')[0], prof.split('　')[-1]  # フルネームを分割
                    professor, _ = Professor.objects.get_or_create(first_name=first_name, last_name=last_name)
                    CourseProfessor.objects.get_or_create(course_schedule=course_schedule, professor=professor)
