from django.contrib import admin

from simulator.models import GroundStation, Satellite, Task


def run_ground_station(modeladmin, request, queryset):
    gs = queryset.first()
    gs.run()
run_ground_station.short_description = "Run selected GroundStation"


def stop_ground_station(modeladmin, request, queryset):
    gs = queryset.first()
    gs.stop()
stop_ground_station.short_description = "Stop selected GroundStation"


def run_satellite(modeladmin, request, queryset):
    for sat in queryset:
        sat.run()
run_satellite.short_description = "Run the selected Satellites."


def dispatch_tasks(modeladmin, request, queryset):
    tasks = queryset.to_dict()
    gs = GroundStation.queryset.first()
    gs.dispatch_tasks(tasks)
dispatch_tasks.short_description = "Dispatch selected tasks to be executed."


class GroundStationAdmin(admin.ModelAdmin):
    actions = [run_ground_station, stop_ground_station]
    list_display = ['hostname', 'port', 'running']


class SatelliteAdmin(admin.ModelAdmin):
    actions = [run_satellite]


class TaskAdmin(admin.ModelAdmin):
    actions = [dispatch_tasks]


admin.site.register(GroundStation, GroundStationAdmin)
admin.site.register(Satellite, SatelliteAdmin)
admin.site.register(Task, TaskAdmin)
