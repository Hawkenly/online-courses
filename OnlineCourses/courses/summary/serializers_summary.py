from rest_framework import serializers


class TaskForStudentSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    task_title = serializers.CharField()
    deadline = serializers.DateTimeField()
    submitted = serializers.BooleanField()
    mark = serializers.IntegerField(allow_null=True)

class LectureForStudentSerializer(serializers.Serializer):
    lecture_id = serializers.IntegerField()
    lecture_name = serializers.CharField()
    tasks = TaskForStudentSerializer(many=True)

class CourseForStudentSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    status = serializers.CharField()
    average_grade = serializers.FloatField(allow_null=True)
    lectures = LectureForStudentSerializer(many=True)

class StudentSummarySerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    courses = CourseForStudentSerializer(many=True)


class CourseForTeacherSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    students_count = serializers.IntegerField()
    average_grade = serializers.FloatField()
    lectures_count = serializers.IntegerField()
    tasks_count = serializers.IntegerField()

class TeacherSummarySerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    courses = CourseForTeacherSerializer(many=True)