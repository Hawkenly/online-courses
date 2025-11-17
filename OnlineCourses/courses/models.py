from django.core.files.uploadedfile import UploadedFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg

from accounts.models import User
from core.models.mixins import CreatedAtMixin, SubmittedAtMixin, RequestedAtMixin, UploadedAtMixin


class Course(CreatedAtMixin):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Lecture(CreatedAtMixin):
    name = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    attachments = models.ManyToManyField('Attachment', blank=True, related_name='lectures')

    def __str__(self):
        return self.name


class Attachment(UploadedAtMixin):
    file = models.FileField(upload_to='attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.file.name


class Task(CreatedAtMixin):
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title


class Solution(SubmittedAtMixin):
    text = models.TextField(blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='solutions')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    mark = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    attachments = models.ManyToManyField(Attachment, blank=True, related_name='solutions')

    def __str__(self):
        return f"Solution by {self.submitted_by} for {self.task}"


class Comment(CreatedAtMixin):
    text = models.TextField()
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.author}"


class Enrollment(RequestedAtMixin):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'},
                                related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.PENDING)
    average_grade = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} in {self.course} ({self.status})"

    def update_average_grade(self):
        avg = Solution.objects.filter(
            submitted_by=self.student,
            task__lecture__course=self.course,
            mark__isnull=False
        ).aggregate(avg_mark=Avg('mark'))['avg_mark']
        self.average_grade = avg
        self.save(update_fields=['average_grade'])
