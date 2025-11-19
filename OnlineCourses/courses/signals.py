import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Solution

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

@receiver(post_save, sender=Solution)
def solution_saved(sender, instance, created, **kwargs):

    if created:
        teacher = instance.task.lecture.course.created_by
        group = f"notifications_user_{teacher.id}"

        payload = {
            "event": "new_solution",
            "solution_id": instance.id,
            "student": instance.submitted_by.username,
            "task": instance.task.title,
        }

        logger.info("Signal: send new_solution to %s payload=%s", group, payload)
        async_to_sync(channel_layer.group_send)(
            group,
            {"type": "notify", "payload": payload}
        )

    else:
        if instance.mark is not None:
            student = instance.submitted_by
            group = f"notifications_user_{student.id}"

            payload = {
                "event": "solution_graded",
                "solution_id": instance.id,
                "mark": instance.mark,
                "task": instance.task.title,
            }

            logger.info("Signal: send solution_graded to %s payload=%s", group, payload)
            async_to_sync(channel_layer.group_send)(
                group,
                {"type": "notify", "payload": payload}
            )
