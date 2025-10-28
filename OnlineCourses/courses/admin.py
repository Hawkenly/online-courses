from django.contrib import admin

from courses.models import Course, Lecture, Task, Solution, Comment, Attachment, Enrollment

admin.site.register([Course, Lecture, Task, Solution, Comment, Attachment, Enrollment])