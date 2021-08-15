from re import T
from django.db.models import Model, IntegerField, CharField, ImageField, DateTimeField, BinaryField
from django.utils.timezone import now

class Chart(Model):
    function_string = CharField(verbose_name='Функция', max_length=128)
    chart_image = BinaryField('График', max_length=2*1042*1024, null=True)
    day_interval = IntegerField(verbose_name='Интервал t, дней')
    hour_step = IntegerField(verbose_name='Шаг t, часы')
    date_process = DateTimeField(verbose_name='Дата обработки', null=True)
    error_message = CharField(verbose_name='Ошибка при обработке данных', max_length=128, null=True)

    def __str__(self):
        return 'chart %s [fucntion - %s, interval - %s, step - %s]' \
            % (self.id, self.function_string, self.day_interval, self.hour_step)