from __future__ import absolute_import

from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

CELERY_RABBITMQ_HOST = '127.0.0.1'
CELERY_RABBITMQ_USER = 'dengbo'
CELERY_RABBITMQ_PASSWORD = '5210'
CELERY_RABBITMQ_PORT = 5672
CELERY_RABBITMQ_VHOST = '/'
BROKER_URL = 'amqp://%s:%s@%s:%d/%s' % (
    CELERY_RABBITMQ_USER, CELERY_RABBITMQ_PASSWORD, CELERY_RABBITMQ_HOST, CELERY_RABBITMQ_PORT, CELERY_RABBITMQ_VHOST)

app = Celery('arrange',
             broker=BROKER_URL,
             include=['tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERYBEAT_SCHEDULE={
        'shovel_shit': {
            'task': 'tasks.send_shovel_shit_task',
            # 'schedule': crontab(minute=0, hour='21,22,23'),
            'schedule': crontab(minute='36,37,38,39',hour='16'),
            # 'schedule': timedelta(seconds=10),

        },
        'on_duty': {
            'task': 'tasks.send_on_duty_task',
            'schedule': crontab(minute=0, hour='11,15,18,22', day_of_week='sat,sun'),
            # 'schedule': crontab(minute='*/1', hour='11,15,18,22,23', day_of_week='sat,sun'),
        }
    }
)

if __name__ == '__main__':
    app.start()
