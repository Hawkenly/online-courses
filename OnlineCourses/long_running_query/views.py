from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .tasks import long_running_query
from .serializers import LongQuerySerializer

@extend_schema(
    summary="Запуск имитации долгого запроса",
    description="Асинхронно запускает задачу через Celery",
    responses={200: LongQuerySerializer},
)
class LongQueryView(APIView):
    serializer_class = LongQuerySerializer

    def get(self, request):
        task = long_running_query.delay()
        return Response({'task_id': task.id, "message" : "Task has been started"}, status=status.HTTP_200_OK)