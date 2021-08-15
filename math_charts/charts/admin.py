import re
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html

import base64
from django.db import transaction

from charts.models import Chart
from celery_proj import tasks


@admin.register(Chart)
class ChartAdmin(ModelAdmin):
    list_display = ('function_string', 'image_tag', 'day_interval', 'hour_step', 'date_process')
    fields = ('function_string', 'day_interval', 'hour_step')

    def image_tag(self, obj):
        if obj.chart_image is not None:
            chart_data = base64.b64encode(obj.chart_image).decode('utf-8')
            return format_html('<img src="%s" width=300 height=300' % ('data:image/png;base64,' + chart_data))
        else:
            return obj.error_message

    image_tag.short_description = 'График'

    def send_image_generate_task(self):
        celery_chart_result = tasks.generate_image.apply_async(args=(self.curr_obj_id,))
        celery_chart_result.get(propagate=False)


    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            self.curr_obj_id = obj.id
            transaction.on_commit(self.send_image_generate_task)