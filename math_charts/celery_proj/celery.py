from celery import Celery
import psycopg2
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('celery_proj', include=['celery_proj.tasks'])
app.config_from_object('django.conf:settings', namespace='CELERY')
