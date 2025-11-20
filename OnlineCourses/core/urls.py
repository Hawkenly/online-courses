from django.urls import path, include

urlpatterns = [
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
    path('', include(('courses.summary.urls_summary', 'summary'), namespace='summary')),
]