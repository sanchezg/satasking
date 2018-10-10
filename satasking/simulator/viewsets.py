from rest_framework import viewsets

from simulator.models import TaskExecution
from simulator.serializers import TaskExecutionSerializer


class TaskExecutionViewSet(viewsets.ModelViewSet):
    """API endpoint that serves the logs of task execution."""
    queryset = TaskExecution.objects.all().order_by('-date_time')
    serializer_class = TaskExecutionSerializer
