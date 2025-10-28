from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg

from accounts.models import User

class Course(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Lecture(models.Model):
    name = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    created_at = models.DateTimeField(auto_now_add=True)
    attachments = models.ManyToManyField('Attachment', blank=True, related_name='lectures')

    def __str__(self):
        return self.name

class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.file.name

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Solution(models.Model):
    text = models.TextField(blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='solutions')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    submitted_at = models.DateTimeField(auto_now_add=True)
    mark = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    attachments = models.ManyToManyField(Attachment, blank=True, related_name='solutions')

    def __str__(self):
        return f"Solution by {self.submitted_by} for {self.task}"

class Comment(models.Model):
    text = models.TextField()
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author}"

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
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