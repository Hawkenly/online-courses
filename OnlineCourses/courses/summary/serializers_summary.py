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


class StudentSummarySerializer(DynamicFieldsModelSerializer):
    id = serializers.IntegerField(source='course_id', read_only=True)
    name = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    average_grade = serializers.FloatField(allow_null=True)
    lectures_count = serializers.IntegerField(read_only=True)
    tasks_count = serializers.IntegerField(read_only=True)
    solved_percentage = serializers.FloatField()

    class Meta:
        model = Enrollment
        fields = ('id', 'name', 'status', 'average_grade', 'lectures_count', 'tasks_count', 'solved_percentage')


class TeacherSummarySerializer(DynamicFieldsModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    average_grade = serializers.FloatField(allow_null=True, read_only=True)
    lectures_count = serializers.IntegerField(read_only=True)
    tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'students_count', 'average_grade', 'lectures_count', 'tasks_count')
