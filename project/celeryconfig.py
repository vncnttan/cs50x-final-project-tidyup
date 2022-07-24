# Credit all tutorial to use celery by Shannon Chan on medium.com
from celery.schedules import crontab

CELERY_IMPORTS = ('tasks', )
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'tasks.daily.email_and_expiredEventClear',
        # Every 00:00 a.m
        'schedule': crontab(minute="*"),
    }
}