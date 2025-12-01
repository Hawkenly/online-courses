from django.urls import path

from courses.summary.views_summary import TeacherSummaryView, StudentSummaryView

urlpatterns = [
    path('teachers/<int:pk>/summary/', TeacherSummaryView.as_view(), name='teacher_summary'),
    path('students/<int:pk>/summary/', StudentSummaryView.as_view(), name='student_summary'),
]