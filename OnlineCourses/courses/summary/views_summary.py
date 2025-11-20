from django.db.models import Q, Prefetch
from django.db.models.aggregates import Count, Avg
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsTeacher
from courses.models import Course, Lecture, Enrollment, Solution
from courses.summary.serializers_summary import TeacherSummarySerializer, StudentSummarySerializer


class TeacherSummaryView(APIView):
    permission_classes = [IsTeacher]

    @extend_schema(
        summary="Get teacher's summary",
        responses={200: TeacherSummarySerializer}
    )
    def get(self, request, pk):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            pass

        elif user.id != pk:
            return Response(
                    {"details" : "You cannot view another teacher's summary."},
            status=status.HTTP_403_FORBIDDEN
            )

        teacher = User.objects.get(pk=pk)

        courses_qs = (Course.objects.filter(created_by=teacher).annotate(
            students_count = Count('enrollments', filter=Q(enrollments__status='approved'), distinct=True),
            lectures_count = Count('lectures', distinct=True),
            average_grade = Avg('enrollments__average_grade'),
            tasks_count = Count('lectures__tasks', distinct=True)
            )
            .prefetch_related(
                Prefetch('lectures', queryset = Lecture.objects.prefetch_related('tasks'),
                ),
            )
        )

        courses_list = []
        for course in courses_qs:
            courses_list.append({
                'course_id': course.id,
                'course_name': course.name,
                'students_count': course.students_count,
                'average_grade': course.average_grade,
                'lectures_count': course.lectures_count,
                'tasks_count': course.tasks_count
            })

        result = {
            "teacher_id": teacher.id,
            "full_name": teacher.full_name,
            "email": teacher.email,
            "courses": courses_list,
        }

        serializer = TeacherSummarySerializer(result)
        return Response(serializer.data)

class StudentSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get student's summary",
        responses={200: StudentSummarySerializer}
    )
    def get(self, request, pk):
        user = self.request.user

        student = User.objects.get(pk=pk)

        if user.is_staff or user.is_superuser:
            pass

        elif getattr(user, 'role', None) == User.RoleTypes.TEACHER:
            has_course = Enrollment.objects.filter(
                student=student,
                course__created_by=user,
                status = Enrollment.Status.APPROVED
            ).exists()

            if not has_course:
                return Response(
                    {"details" : "You cannot view not your student's summary."},
                status=status.HTTP_403_FORBIDDEN
                )

        elif user.id != pk:
            return Response(
                {"details" : "You cannot view another student's summary."},
            status=status.HTTP_403_FORBIDDEN
            )

        enrollments_qs = (Enrollment.objects.filter(student = student, status = Enrollment.Status.APPROVED)
                    .select_related('course')
                    .prefetch_related(Prefetch(
                                 'course__lectures',
                                         queryset = Lecture.objects.prefetch_related('tasks')
                                )
                    )
        )

        task_ids = set()
        for enrollment in enrollments_qs:
            for lecture in enrollment.course.lectures.all():
                for task in lecture.tasks.all():
                    task_ids.add(task.id)

        solutions = (
            Solution.objects
            .filter(submitted_by=student, task_id__in=task_ids)
            .select_related("submitted_by")
        )

        solution_by_task_id = {solution.task_id: solution for solution in solutions}

        courses_list = []

        for enrollment in enrollments_qs:
            course = enrollment.course
            lectures_list = []

            for lecture in course.lectures.all():
                tasks_list = []

                for task in lecture.tasks.all():
                    solution = solution_by_task_id.get(task.id)

                    tasks_list.append({
                        'task_id': task.id,
                        'task_title': task.title,
                        'deadline': task.deadline,
                        'submitted': solution is not None,
                        'mark': solution.mark if solution is not None else None,
                    })

                lectures_list.append({
                    'lecture_id': lecture.id,
                    'lecture_name': lecture.name,
                    'tasks': tasks_list,
                })

            courses_list.append({
                'course_id': course.id,
                'course_name': course.name,
                'status': enrollment.status,
                'average_grade': enrollment.average_grade,
                'lectures': lectures_list,
            })

        result = {
            "student_id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "courses": courses_list,
        }

        serializer = StudentSummarySerializer(result)
        return Response(serializer.data)






