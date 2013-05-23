'''
Created on May 21, 2013

@author: kidio
'''
'''
At this point, if you try to push the app with a different name , 
you will see database connection errors. Let’s see why, and how to avoid that!

On dotCloud, you get your own MongoDB instance. This is not just a database inside
 an existing MongoDB server: it is your own MongoDB server. This eliminates access contention 
 and side effects caused by other users. However, it also means that when you deploy a MongoDB service, 
 you will have to wait a little bit while MongoDB pre-allocates some disk storage for you. This takes about one minute.

If you did the tutorial step by step, you probably did not notice that, since there was probably more than 
one minute between your first push, and your first attempt to use the database. But if you try to push all 
the code again, it will try to connect to the database straight away, and fail.

To avoid connection errors (which could happen if we try to connect to the server before it’s done with 
space pre-allocation), we add a small helper script, waitfordb.py, which will just try to connect every 10 seconds.
It exists as soon as the connection is successful. If the connection fails after 10 minutes, it aborts (as a failsafe 
feature).
'''
#!/usr/bin/env python
from wsgi import *
from django.contrib.auth.models import User
from pymongo.errors import AutoReconnect
import time
deadline = time.time() + 600
while time.time() < deadline:
    try:
        User.objects.count()
        print 'Successfully connected to database.'
        exit(0)
    except AutoReconnect:
        print 'Could not connect to database. Waiting a little bit.'
        time.sleep(10)
    except ConfigurationError:
        print 'Could not connect to database. Waiting a little bit.'
        time.sleep(10)
print 'Could not connect to database after 10 minutes. Something is wrong.'
exit(1)