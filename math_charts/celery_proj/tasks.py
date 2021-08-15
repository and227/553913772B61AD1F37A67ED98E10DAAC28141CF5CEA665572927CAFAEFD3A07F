from .celery import app
from .logic import save_image_to_db


@app.task
def generate_image(id):
    return save_image_to_db(id)

