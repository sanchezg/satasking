from rest_framework import serializers

from simulator.models import Satellite, Task, TaskExecution


class SatelliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Satellite
        fields = ('name', 'resources')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('name', 'payoff', 'resources')


class TaskExecutionSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    satellite = SatelliteSerializer(read_only=True)
    date_time = serializers.DateTimeField(format='iso-8601')

    class Meta:
        model = TaskExecution
        fields = ('task', 'satellite', 'date_time')
