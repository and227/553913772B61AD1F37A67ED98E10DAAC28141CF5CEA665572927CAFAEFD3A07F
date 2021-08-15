import datetime
import re
import requests
import os
import json
import psycopg2
from math import sin, cos, tan, asin, acos, atan, sqrt

supported_tokens = ['t', '(', ')', '+', '-', '*', '/', 'sqrt', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan']

eval_glob = {
    'sin': sin,
    'cos': cos,
    'tan': tan,
    'asin': asin,
    'acos': acos,
    'atan': atan,
    'sqrt': sqrt
}

def ckeck_expression(in_str):
    current_token = ''
    token_finded = False
    str_pointer = 0

    while str_pointer < len(in_str):
        current_token += in_str[str_pointer]
        if current_token.isdigit() or current_token in supported_tokens:
            token_finded = True
            current_token = ''
        str_pointer += 1
    
    if not token_finded:
        return False

    return True


def get_func_data(in_str, interval, step):
    time_points = list()
    data_points = list()
    expr = re.sub(r'\s+', '', in_str)
    if expr.startswith('y='):
        expr = expr.lstrip('y=')
        if ckeck_expression(expr):
            try:
                end = datetime.datetime.now()
                print(end)
                start = end - datetime.timedelta(days=interval)
                print(start)
                time_points = [start + datetime.timedelta(hours=t) for t in range(0, (end-start).days*24, step)]
                time_points = [int(t.strftime('%s')) for t in time_points]
                data_points = [eval(expr, eval_glob, {'t': t}) for t in time_points]
            except SyntaxError as e:
                raise ValueError(f'Not supported expression: {in_str}')
        else:
            raise ValueError(f'Not supported expression: {in_str}')
    else:
        raise ValueError(f'Not supported expression: {in_str}')

    return time_points, data_points


def connect_db(func):
    def wrapped(*args, **kwargs):
        celery_db_connection = psycopg2.connect(
            database=os.getenv('POSTGRES_DB'), 
            user=os.getenv('POSTGRES_USER'), 
            password=os.getenv('POSTGRES_PASSWORD'), 
            host=os.getenv('POSTGRES_SERVER'), 
            port=os.getenv('POSTGRES_PORT')
        )
        cursor = celery_db_connection.cursor()
        func(cursor, *args, **kwargs)
        celery_db_connection.commit()
        celery_db_connection.close()

    return wrapped


def get_image(y_vals, t_vals):
    response = requests.post(
        url=f"http://{os.getenv('HIGHCHARTS_SERVER')}:{os.getenv('HIGHCHARTS_PORT')}",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "infile": {
                "title": {
                    "text": "Steep Chart"
                },
                "xAxis": {
                    "hours": y_vals
                },
                "series": [
                    { "data": t_vals }
                ]
            }
        })
    )
    return response


@connect_db
def save_image_to_db(cursor, id):
    ret_state = ''
    query = 'select function_string, day_interval, hour_step from charts_chart where id = %s;'
    cursor.execute(query=query, vars=(id,))
    image_data = cursor.fetchone()
    if image_data is not None:
        try:
            y_vals, t_vals = get_func_data(image_data[0], image_data[1], image_data[2])
            response = get_image(y_vals, t_vals)
            query = 'update charts_chart set chart_image = %s, date_process = %s where id = %s'               
            cursor.execute(query=query, vars=(response.content, datetime.datetime.now(), id))
            ret_state = 'SUCCESS'
        except Exception as e:
            query = 'update charts_chart set error_message = %s, date_process = %s where id = %s'
            cursor.execute(query=query, vars=(str(e), datetime.datetime.now(), id))
            ret_state = 'ERROR'
    else:
        ret_state = 'ERROR' 

    return ret_state
