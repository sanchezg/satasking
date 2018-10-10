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
run_satellite.short_description = "Run selected satellites"


def stop_satellite(modeladmin, request, queryset):
    for sat in queryset:
        sat.stop()
stop_satellite.short_description = "Stop selected satellites"


def dispatch_tasks(modeladmin, request, queryset):
    tasks = list(queryset)
    gs = GroundStation.objects.first()
    gs.dispatch_tasks(tasks)
dispatch_tasks.short_description = "Dispatch selected tasks to satellites"


class GroundStationAdmin(admin.ModelAdmin):
    actions = [run_ground_station, stop_ground_station]
    list_display = ['hostname', 'port', 'running']


class SatelliteAdmin(admin.ModelAdmin):
    actions = [run_satellite, stop_satellite]
    list_display = ['name', 'hostname', 'port', 'resources', 'running']


class TaskAdmin(admin.ModelAdmin):
    actions = [dispatch_tasks]
    list_display = ['name', 'payoff', 'resources']


admin.site.register(GroundStation, GroundStationAdmin)
admin.site.register(Satellite, SatelliteAdmin)
admin.site.register(Task, TaskAdmin)
