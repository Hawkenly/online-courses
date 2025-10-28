from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CourseViewSet, LectureViewSet, TaskViewSet, SolutionViewSet, CommentViewSet,
                    AttachmentViewSet, EnrollmentViewSet)

router = DefaultRouter()
router.register('courses', CourseViewSet)
router.register('lectures', LectureViewSet)
router.register('tasks', TaskViewSet)
router.register('solutions', SolutionViewSet)
router.register('comments', CommentViewSet)
router.register('attachments', AttachmentViewSet)
router.register('enrollments', EnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]