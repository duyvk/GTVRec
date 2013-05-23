'''
Created on May 21, 2013

@author: kidio
'''
#!/usr/bin/env python
from wsgi import *
from django.contrib.auth.models import User
u, created = User.objects.get_or_create(username='admin')
if created:
    u.set_password('1')
    u.is_superuser = True
    u.is_staff = True
    u.save()