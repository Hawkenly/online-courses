from django.db import models
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from drf_spectacular.utils import extend_schema_view, extend_schema

from accounts.models import User
from .models import Course, Lecture, Task, Solution, Comment, Attachment, Enrollment
from .serializers import (
    CourseSerializer, CourseCreateSerializer, CourseListSerializer,
    LectureSerializer, CreateLectureSerializer,
    TaskSerializer, CreateTaskSerializer,
    SolutionSerializer, CreateSolutionSerializer, SolutionMarkSerializer,
    CommentSerializer, AttachmentSerializer, AttachmentCreateSerializer,
    EnrollmentSerializer, EnrollmentCreateSerializer
)
from accounts.permissions import IsTeacher, IsStudent

@extend_schema_view(
    list=extend_schema(summary="List courses", tags=['Courses'], responses=CourseListSerializer),
    retrieve=extend_schema(summary="Retrieve course", tags=['Courses'], responses=CourseSerializer),
    create=extend_schema(summary="Create course (teacher only)", tags=['Courses'], request=CourseCreateSerializer,
                         responses=CourseSerializer),
    update=extend_schema(summary="Update course (teacher only)", tags=['Courses'], request=CourseCreateSerializer,
                         responses=CourseSerializer),
    partial_update=extend_schema(summary="Partial update course (teacher only)", tags=['Courses'],
                                 request=CourseCreateSerializer, responses=CourseSerializer),
    destroy=extend_schema(summary="Delete course (teacher only)", tags=['Courses']),
)
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        if self.action == 'create':
            return CourseCreateSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacher()]
        return [IsAuthenticated()]


@extend_schema_view(
    list=extend_schema(summary="List lectures (only lectures of courses you have access to)", tags=['Lectures']),
    retrieve=extend_schema(summary="Retrieve lecture", tags=['Lectures'], responses=LectureSerializer),
    create=extend_schema(summary="Create lecture (teacher only)", tags=['Lectures'], request=CreateLectureSerializer,
                         responses=LectureSerializer),
    update=extend_schema(summary="Update lecture (teacher only)", tags=['Lectures'], request=CreateLectureSerializer,
                         responses=LectureSerializer),
    partial_update=extend_schema(summary="Partial update lecture (teacher only)", tags=['Lectures'],
                                 request=CreateLectureSerializer, responses=LectureSerializer),
    destroy=extend_schema(summary="Delete lecture (teacher only)", tags=['Lectures']),
)
class LectureViewSet(ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateLectureSerializer
        return LectureSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Lecture.objects.all()

        if getattr(user, "role", None) == User.RoleTypes.TEACHER:
            return Lecture.objects.filter(course__created_by=user)

        approved_course_ids = Enrollment.objects.filter(
            student=user,
            status=Enrollment.Status.APPROVED
        ).values_list('course_id', flat=True)

        return Lecture.objects.filter(course_id__in=approved_course_ids).distinct()

    def perform_create(self, serializer):
        lecture = serializer.save()
        attachments = self.request.data.get('attachments')
        if attachments:
            lecture.attachments.set(attachments)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacher()]
        return [IsAuthenticated()]

@extend_schema_view(
    list=extend_schema(summary="List tasks (only tasks of courses you have access to)", tags=['Tasks']),
    retrieve=extend_schema(summary="Retrieve task", tags=['Tasks'], responses=TaskSerializer),
    create=extend_schema(summary="Create task (teacher only)", tags=['Tasks'], request=CreateTaskSerializer,
                         responses=TaskSerializer),
    update=extend_schema(summary="Update task (teacher only)", tags=['Tasks'], request=CreateTaskSerializer,
                         responses=TaskSerializer),
    partial_update=extend_schema(summary="Partial update task (teacher only)", tags=['Tasks'],
                                 request=CreateTaskSerializer, responses=TaskSerializer),
    destroy=extend_schema(summary="Delete task (teacher only)", tags=['Tasks']),
)
class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTaskSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Task.objects.all()

        if getattr(user, "role", None) == User.RoleTypes.TEACHER:
            return Task.objects.filter(lecture__course__created_by=user)

        approved_course_ids = Enrollment.objects.filter(
            student=user,
            status=Enrollment.Status.APPROVED
        ).values_list('course_id', flat=True)

        return Task.objects.filter(lecture__course_id__in=approved_course_ids).distinct()

    def perform_create(self, serializer):
        serializer.save()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacher()]
        return [IsAuthenticated()]


@extend_schema_view(
    list=extend_schema(summary="List solutions (teachers see course solutions; students see their own)",
                       tags=['Solutions']),
    retrieve=extend_schema(summary="Retrieve solution", tags=['Solutions'], responses=SolutionSerializer),
    create=extend_schema(summary="Submit solution (student only, must be enrolled & approved)", tags=['Solutions'],
                         request=CreateSolutionSerializer, responses=SolutionSerializer),
    update=extend_schema(summary="Set mark (teacher only)", tags=['Solutions'], request=SolutionMarkSerializer,
                         responses=SolutionSerializer),
    partial_update=extend_schema(summary="Set mark (teacher only)", tags=['Solutions'], request=SolutionMarkSerializer,
                                 responses=SolutionSerializer),
    destroy=extend_schema(summary="Delete solution (teacher only)", tags=['Solutions']),
)
class SolutionViewSet(ModelViewSet):
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSolutionSerializer
        if self.action in ['update', 'partial_update']:
            return SolutionMarkSerializer
        return SolutionSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsStudent()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Solution.objects.all()
        if getattr(user, 'role', None) == User.RoleTypes.TEACHER:
            return Solution.objects.filter(task__lecture__course__created_by=user)
        return Solution.objects.filter(submitted_by=user)

    def perform_create(self, serializer):
        task = serializer.validated_data['task']
        user = self.request.user
        if task.deadline < timezone.now():
            raise ValidationError("Deadline passed")

        try:
            enrollment = Enrollment.objects.get(student=user, course=task.lecture.course)
        except Enrollment.DoesNotExist:
            raise PermissionDenied("You are not enrolled in this course.")
        if enrollment.status != Enrollment.Status.APPROVED:
            raise PermissionDenied("Your enrollment is not approved; you cannot submit solutions.")

        last_solution = Solution.objects.filter(task=task, submitted_by=user).order_by('submitted_at').last()
        if last_solution and last_solution.mark is None:
            raise ValidationError("Previous solution not graded")

        solution = serializer.save(submitted_by=user)
        attachments = serializer.validated_data.get('attachments', [])
        if attachments:
            solution.attachments.set(attachments)

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.mark is not None:
            try:
                enrollment = Enrollment.objects.get(student=instance.submitted_by, course=instance.task.lecture.course)
                enrollment.update_average_grade()
            except Enrollment.DoesNotExist:
                pass


@extend_schema_view(
    list=extend_schema(summary="List comments (only comments user can access)", tags=['Comments']),
    retrieve=extend_schema(summary="Retrieve comment", tags=['Comments'], responses=CommentSerializer),
    create=extend_schema(summary="Create comment (only participants or teacher)", tags=['Comments'],
                         request=CommentSerializer, responses=CommentSerializer),
    update=extend_schema(summary="Update comment", tags=['Comments'], request=CommentSerializer,
                         responses=CommentSerializer),
    partial_update=extend_schema(summary="Partial update comment", tags=['Comments'], request=CommentSerializer,
                                 responses=CommentSerializer),
    destroy=extend_schema(summary="Delete comment", tags=['Comments']),
)
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Comment.objects.all()
        if getattr(user, 'role', None) == User.RoleTypes.TEACHER:
            return Comment.objects.filter(solution__task__lecture__course__created_by=user)
        return Comment.objects.filter(
            models.Q(solution__submitted_by=user) |
            models.Q(solution__task__lecture__course__enrollments__student=user,
                     solution__task__lecture__course__enrollments__status='approved')
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        solution = serializer.validated_data.get('solution')
        course = solution.task.lecture.course

        if getattr(user, 'role', None) == User.RoleTypes.TEACHER:
            if course.created_by != user and not user.is_staff:
                raise PermissionDenied("Only teacher of this course can comment.")
            serializer.save(author=user)
            return

        if solution.submitted_by == user:
            serializer.save(author=user)
            return

        try:
            enrollment = Enrollment.objects.get(student=user, course=course)
        except Enrollment.DoesNotExist:
            raise PermissionDenied("You are not enrolled in this course.")
        if enrollment.status != Enrollment.Status.APPROVED:
            raise PermissionDenied("Your enrollment is not approved; you cannot comment.")
        serializer.save(author=user)

@extend_schema_view(
    list=extend_schema(summary="List attachments (only attachments user can access)", tags=['Attachments']),
    retrieve=extend_schema(summary="Retrieve attachment", tags=['Attachments'], responses=AttachmentSerializer),
    create=extend_schema(summary="Upload attachment", tags=['Attachments'], request=AttachmentCreateSerializer,
                         responses=AttachmentSerializer),
    destroy=extend_schema(summary="Delete attachment", tags=['Attachments']),
)
class AttachmentViewSet(ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Attachment.objects.all()

        if getattr(user, 'role', None) == User.RoleTypes.TEACHER:
            return Attachment.objects.filter(
                models.Q(lectures__course__created_by=user) |
                models.Q(solutions__task__lecture__course__created_by=user)
            ).distinct()

        return Attachment.objects.filter(
            models.Q(uploaded_by=user) |
            models.Q(solutions__submitted_by=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="List enrollments", tags=['Enrollments'], responses=EnrollmentSerializer),
    retrieve=extend_schema(summary="Retrieve enrollment", tags=['Enrollments'], responses=EnrollmentSerializer),
    create=extend_schema(summary="Student requests enrollment (student only) or teacher may add student",
                         tags=['Enrollments'], request=EnrollmentCreateSerializer, responses=EnrollmentSerializer),
    update=extend_schema(summary="Update enrollment (teacher actions)", tags=['Enrollments'],
                         request=EnrollmentCreateSerializer, responses=EnrollmentSerializer),
    partial_update=extend_schema(summary="Partial update enrollment (teacher actions)", tags=['Enrollments'],
                                 request=EnrollmentCreateSerializer, responses=EnrollmentSerializer),
    destroy=extend_schema(summary="Delete enrollment", tags=['Enrollments']),
)
class EnrollmentViewSet(ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return EnrollmentCreateSerializer
        return EnrollmentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy', 'approve', 'reject']:
            return [ IsTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) == User.RoleTypes.STUDENT:
            serializer.save(student=user, status=Enrollment.Status.PENDING)
        elif getattr(user, "role", None) == User.RoleTypes.TEACHER:
            instance = serializer.save()
            if instance.status == Enrollment.Status.APPROVED:
                instance.update_average_grade()
        else:
            raise PermissionDenied("Only students or teachers can create enrollments.")

    @extend_schema(
        summary="Approve enrollment (teacher only)",
        tags=['Enrollments'],
        responses={200: EnrollmentSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsTeacher])
    def approve(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.status = Enrollment.Status.APPROVED
        enrollment.save(update_fields=['status'])
        enrollment.update_average_grade()
        return Response({'status': 'approved'})

    @extend_schema(
        summary="Reject enrollment (teacher only)",
        tags=['Enrollments'],
        responses={200: EnrollmentSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsTeacher])
    def reject(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.status = Enrollment.Status.REJECTED
        enrollment.save(update_fields=['status'])
        return Response({'status': 'rejected'})

    def perform_update(self, serializer):
        prev_instance = self.get_object()
        instance = serializer.save()
        instance.update_average_grade()
