from django.db import models\

class CreatedAtMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
class UploadedAtMixin(models.Model):
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SubmittedAtMixin(models.Model):
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class RequestedAtMixin(models.Model):
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True