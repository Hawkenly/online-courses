from django.db.models import Q, Prefetch
from django.db.models.aggregates import Count, Avg
from django.utils.text import capfirst
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsTeacher
from courses.models import Course, Lecture, Enrollment, Solution
from courses.summary.serializers_summary import TeacherSummarySerializer, StudentSummarySerializer


class TablePagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

def infer_col_meta_from_model(model, field_name):
    try:
        field = model._meta.get_field(field_name)
        label = capfirst(getattr(field, 'verbose_name', field_name))
        internal_type = field.get_internal_type().lower()
        if internal_type in ('integerfield', 'bigintegerfield', 'smallintegerfield', 'positiveintegerfield'):
            t = 'number'
        elif internal_type in ('floatfield', 'decimalfield'):
            t = 'number'
        elif internal_type in ('booleanfield',):
            t = 'boolean'
        elif internal_type in ('datefield', 'datetimefield', 'timefield'):
            t = 'date'
        else:
            t = 'string'
        return {'key': field_name, 'label': str(label), 'type': t, 'sortable': True}
    except Exception:
        return {'key': field_name, 'label': field_name.replace('_', ' ').title(), 'type': 'string', 'sortable': True}


class TeacherSummaryView(GenericAPIView):
    permission_classes = [IsTeacher]
    pagination_class = TablePagination
    serializer_class = TeacherSummarySerializer

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

        requested = None
        fields_param = request.query_params.get('fields')
        if fields_param:
            requested = [f.strip() for f in fields_param.split(',') if f.strip()]

        sort = request.query_params.get('sort')
        all_fields = {'id', 'name', 'students_count', 'average_grade', 'lectures_count', 'tasks_count'}
        allowed_sort_fields = set(requested) & all_fields if requested else all_fields
        order_by = None

        if sort:
            if sort.startswith('-'):
                s = sort[1:]
                prefix = '-'
            else:
                s = sort
                prefix = ''
            if s in allowed_sort_fields:
                order_by = prefix + s
            else:
                order_by = None

        if order_by:
            courses_qs = courses_qs.order_by(order_by)

        page = self.paginate_queryset(courses_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=requested)
            courses_serialized = serializer.data
        else:
            serializer = self.get_serializer(courses_qs, many=True, fields=requested)
            courses_serialized = serializer.data

        data = courses_serialized

        cols_keys = requested if requested is not None else list(serializer.child.fields.keys())
        cols = []
        for f in cols_keys:
            col_meta = infer_col_meta_from_model(Course, f)
            col_meta['sortable'] = (f in allowed_sort_fields)
            cols.append(col_meta)

        owner = {
            'teacher_id': teacher.id,
            'full_name': teacher.full_name,
            'email': getattr(teacher, 'email', None)
        }

        paginator = self.paginator
        meta = {
            'total': paginator.page.paginator.count if getattr(paginator, 'page', None) is not None else courses_qs.count(),
            'page': paginator.page.number if getattr(paginator, 'page', None) is not None else 1,
            'page_size': paginator.get_page_size(request),
            'sort': sort or ""
        }

        return Response({
            'owner': owner,
            'meta': meta,
            'data': data,
            'cols': cols
        })


class StudentSummaryView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = TablePagination
    serializer_class = StudentSummarySerializer

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

        requested = None
        fields_param = request.query_params.get('fields')
        if fields_param:
            requested = [f.strip() for f in fields_param.split(',') if f.strip()]

        sort = request.query_params.get('sort')
        all_fields = {'id', 'name', 'status', 'average_grade', 'lectures_count', 'tasks_count'}
        allowed_sort_fields = set(requested) & all_fields if requested else all_fields
        order_by = None

        if sort:
            if sort.startswith('-'):
                s = sort[1:]
                prefix = '-'
            else:
                s = sort
                prefix = ''
            if s in allowed_sort_fields:
                order_by = prefix + s
            else:
                order_by = None

        if order_by:
            enrollments_qs = enrollments_qs.order_by(order_by)

        page = self.paginate_queryset(enrollments_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=requested)
            enrollments_serialized = serializer.data
        else:
            serializer = self.get_serializer(enrollments_qs, many=True, fields=requested)
            enrollments_serialized = serializer.data

        data = enrollments_serialized

        cols_keys = requested if requested is not None else list(serializer.child.fields.keys())
        cols = []
        for f in cols_keys:
            col_meta = infer_col_meta_from_model(Course, f)
            col_meta['sortable'] = (f in allowed_sort_fields)
            cols.append(col_meta)

        owner = {
            'student_id': student.id,
            'full_name': student.full_name,
            'email': getattr(student, 'email', None)
        }

        paginator = self.paginator
        meta = {
            'total': paginator.page.paginator.count if getattr(paginator, 'page',
                                                               None) is not None else enrollments_qs.count(),
            'page': paginator.page.number if getattr(paginator, 'page', None) is not None else 1,
            'page_size': paginator.get_page_size(request),
            'sort': sort or ""
        }

        return Response({
            'owner': owner,
            'meta': meta,
            'data': data,
            'cols': cols
        })