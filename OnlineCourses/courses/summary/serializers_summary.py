from rest_framework import serializers

from courses.models import Course, Enrollment


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


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

class StudentSummarySerializer(DynamicFieldsModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField(read_only=True)
    average_grade = serializers.FloatField(allow_null=True)
    lectures_count = serializers.IntegerField()
    tasks_count = serializers.IntegerField()

    class Meta:
        model = Enrollment
        fields = ('id', 'name', 'status', 'average_grade', 'lectures_count', 'tasks_count')


class TeacherSummarySerializer(DynamicFieldsModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    students_count = serializers.IntegerField()
    average_grade = serializers.FloatField(allow_null=True)
    lectures_count = serializers.IntegerField()
    tasks_count = serializers.IntegerField()

    class Meta:
        model = Course
        fields = ('id', 'name', 'students_count', 'average_grade', 'lectures_count', 'tasks_count')
