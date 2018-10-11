import os, sys
sys.path.append('.')

os.environ['DJANGO_SETTINGS_MODULE'] = 'satasking.settings'
import django
django.setup()

from simulator.models import GroundStation, Satellite, Task


gs = GroundStation.objects.create()

tasks = [
    Task(name='t1', payoff='10', resources='1,2,3'),
    Task(name='t2', payoff='20', resources='1,3,4,5'),
    Task(name='t3', payoff='30', resources='2,4,8'),
    Task(name='t4', payoff='40', resources='3,4,5,6'),
    Task(name='t5', payoff='50', resources='1'),
    Task(name='t6', payoff='60', resources='8,9'),
    Task(name='t7', payoff='70', resources='7,9'),
    Task(name='t8', payoff='80', resources='4,8'),
    Task(name='t9', payoff='90', resources='1,3,5,9'),
    Task(name='t10', payoff='100', resources='1,2,7'),
]
ts = Task.objects.bulk_create(tasks)

satellites = [
    Satellite(name='s1', resources='1,2,3'),
    Satellite(name='s2', resources='1,3,4,5'),
    Satellite(name='s3', resources='2,4,8'),
    Satellite(name='s4', resources='3,4,5,6'),
    Satellite(name='s5', resources='1'),
    Satellite(name='s6', resources='8,9'),
    Satellite(name='s7', resources='7,9'),
    Satellite(name='s8', resources='4,8'),
    Satellite(name='s9', resources='1,3,5,9'),
    Satellite(name='s10', resources='1,2,7'),
]
ss = Satellite.objects.bulk_create(satellites)

print("Succesfully created instances")
