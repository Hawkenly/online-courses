from django.urls import path, include

urlpatterns = [
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
    path('external/', include(('external_api.urls', 'external_api'), namespace='external_api')),
]