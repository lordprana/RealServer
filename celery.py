from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, Task

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealServer.settings')

app = Celery('RealServer')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

class TransactionAwareTask(Task):
    '''
    Task class which is aware of django db transactions and only executes tasks
    after transaction has been committed
    '''
    abstract = True

    def apply_async(self, *args, **kwargs):
        '''
        Unlike the default task in celery, this task does not return an async
        result
        '''
        transaction.on_commit(
            lambda: super(TransactionAwareTask, self).apply_async(
                *args, **kwargs))