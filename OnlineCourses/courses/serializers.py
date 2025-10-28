from rest_framework import serializers
from django.utils import timezone

from .models import Course, Lecture, Task, Solution, Comment, Attachment, Enrollment
from accounts.serializers import UserSerializer
from accounts.models import User


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at', 'uploaded_by']


class AttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'solution', 'author', 'created_at']
        read_only_fields = ['author', 'created_at']


class SolutionSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    submitted_by = UserSerializer(read_only=True)

    class Meta:
        model = Solution
        fields = ['id', 'text', 'task', 'submitted_by', 'submitted_at', 'mark', 'comments', 'attachments']
        read_only_fields = ['submitted_by', 'submitted_at', 'task', 'comments', 'attachments']


class CreateSolutionSerializer(serializers.ModelSerializer):
    attachments = serializers.PrimaryKeyRelatedField(queryset=Attachment.objects.all(), many=True, required=False)

    class Meta:
        model = Solution
        fields = ['id', 'text', 'task', 'attachments']

    def validate_task(self, value):
        if value.deadline < timezone.now():
            raise serializers.ValidationError("Deadline passed for this task.")
        return value

    def validate(self, attrs):
        task = attrs.get('task')
        user = self.context['request'].user
        last = Solution.objects.filter(task=task, submitted_by=user).order_by('submitted_at').last()
        if last and last.mark is None:
            raise serializers.ValidationError("Previous solution is not graded yet; cannot submit a new one.")
        return attrs


class SolutionMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ['id', 'mark']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    solutions = SolutionSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'deadline', 'lecture', 'created_at', 'solutions']
        read_only_fields = ['created_at', 'solutions']


class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'deadline', 'lecture']


class LectureSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Lecture
        fields = ['id', 'name', 'text', 'course', 'created_at', 'tasks', 'attachments']
        read_only_fields = ['created_at', 'tasks', 'attachments']


class CreateLectureSerializer(serializers.ModelSerializer):
    attachments = serializers.PrimaryKeyRelatedField(queryset=Attachment.objects.all(), many=True, required=False)

    class Meta:
        model = Lecture
        fields = ['id', 'name', 'text', 'course', 'attachments']


class CourseSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    lectures = LectureSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'created_by', 'created_at', 'lectures']
        read_only_fields = ['created_by', 'created_at', 'lectures']


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name']


class CourseListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'created_by', 'created_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'status', 'requested_at', 'average_grade']
        read_only_fields = ['requested_at', 'average_grade', 'student', 'course']


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student'), required=False)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'status']
        extra_kwargs = {
            'status': {'required': False}
        }

    def validate(self, attrs):
        student = attrs.get('student')
        course = attrs.get('course')
        request_user = self.context['request'].user
        if not student:
            if request_user.role != 'student':
                raise serializers.ValidationError("Student must be specified when creating enrollment as teacher.")
            student = request_user
            attrs['student'] = student
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("Enrollment already exists for this student and course.")
        return attrs
