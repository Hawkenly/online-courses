from django.urls import path, include

urlpatterns = [
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
    path('long_query/', include(('long_running_query.urls', 'long_query'), namespace='long_query')),
]